import asyncio
import os
import logging
from dotenv import load_dotenv
from datetime import datetime
from pathlib import Path
import shutil

from azure.identity.aio import DefaultAzureCredential
from azure.ai.projects.aio import AIProjectClient
from azure.ai.projects.models import FunctionTool, ToolSet, ConnectedAgentTool
from log_plugin import log_functions
from devops_plugin import devops_functions

# Import logging configuration
from log_util import LogUtil, vdebug

# Load environment variables early
load_dotenv()

# Read logging configuration from environment
verbose_output = os.getenv("VERBOSE_OUTPUT", "false") == "true"

# Setup logging with explicit parameters
logging_config = LogUtil()
logging_config.setup_logging(verbose=verbose_output)

INCIDENT_MANAGER = "INCIDENT_MANAGER"
INCIDENT_MANAGER_INSTRUCTIONS = """
Analyze the given log file or the response from the devops assistant.
Recommend which one of the following actions should be taken:

Restart service {service_name}
Rollback transaction
Redeploy resource {resource_name}
Increase quota

If there are no issues or if the issue has already been resolved, respond with "No action needed."
If none of the options resolve the issue, respond with "Escalate issue."

RULES:
- Do not perform any corrective actions yourself.
- Read the log file on every turn.
- Prepend your response with this text: "INCIDENT_MANAGER > {logfilepath} | "
- Only respond with the corrective action instructions.
"""

DEVOPS_ASSISTANT = "DEVOPS_ASSISTANT"
DEVOPS_ASSISTANT_INSTRUCTIONS = """
Read the instructions from the INCIDENT_MANAGER and apply the appropriate resolution function. 
Return the response as "{function_response}"
If the instructions indicate there are no issues or actions needed, 
take no action and respond with "No action needed."

RULES:
- Use the instructions provided.
- Do not read any log files yourself.
- Prepend your response with this text: "DEVOPS_ASSISTANT > "
"""

async def main():
    logging.info("Starting incident resolution process...")

    # Get the log files
    logging.info("Getting log files...")
    script_dir = Path(__file__).parent
    src_path = script_dir / "sample_logs"
    file_path = script_dir / "logs"
    shutil.copytree(src_path, file_path, dirs_exist_ok=True)
    logging.info(f"Log files copied to: {file_path}")

    # Read the model deployment name from the environment variable
    project_endpoint = os.getenv("PROJECT_ENDPOINT")
    model_deployment = os.getenv("MODEL_DEPLOYMENT_NAME")
    
    if not project_endpoint or not model_deployment:
        logging.warning("Environment variables PROJECT_ENDPOINT or MODEL_DEPLOYMENT_NAME are missing.")
    else:
        logging.info(f"Using project endpoint: {project_endpoint}")
        logging.info(f"Using model deployment: {model_deployment}")

    logging.info("Initializing AIProjectClient...")
    async with (
        DefaultAzureCredential(
            exclude_environment_credential=True,
            exclude_managed_identity_credential=True) as creds,
        AIProjectClient(
            endpoint=project_endpoint,
            credential=creds
        ) as client,
    ):
        logging.info("AIProjectClient initialized.")
        
        # Create function tools for log reading
        logging.info("Creating function tools for log reading...")
        log_tool = FunctionTool(log_functions)
        log_toolset = ToolSet()
        log_toolset.add(log_tool)
        logging.debug(f"Log function tools created: {len(log_functions)} functions")
        
        # Create the incident manager agent on the Azure AI agent service
        logging.info("Creating incident manager agent...")
        incident_agent = await client.agents.create_agent(
            model=model_deployment,
            name=INCIDENT_MANAGER,
            instructions=INCIDENT_MANAGER_INSTRUCTIONS,
            toolset=log_toolset
        )
        logging.info(f"Incident manager agent created: id={incident_agent.id}")

        # Create function tools for devops operations
        logging.info("Creating function tools for devops operations...")
        devops_tool = FunctionTool(devops_functions)
        devops_toolset = ToolSet()
        devops_toolset.add(devops_tool)
        logging.debug(f"DevOps function tools created: {len(devops_functions)} functions")
        
        # Create the devops agent on the Azure AI agent service
        logging.info("Creating devops assistant agent...")
        devops_agent = await client.agents.create_agent(
            model=model_deployment,
            name=DEVOPS_ASSISTANT,
            instructions=DEVOPS_ASSISTANT_INSTRUCTIONS,
            toolset=devops_toolset
        )
        logging.info(f"DevOps assistant agent created: id={devops_agent.id}")

        # Create a connected agent tool for the devops assistant
        devops_connected_tool = ConnectedAgentTool(
            id=devops_agent.id,
            name=DEVOPS_ASSISTANT,
            description="Performs devops operations like restart service, rollback transaction, redeploy resource, increase quota, or escalate issue"
        )
        
        # Create orchestrator agent that coordinates the two agents
        logging.info("Creating orchestrator agent...")
        orchestrator_agent = await client.agents.create_agent(
            model=model_deployment,
            name="orchestrator",
            instructions=f"""You are an orchestrator that coordinates incident management.
            
When given a log file path:
1. First, analyze the log file yourself to understand the issue
2. Then call the {DEVOPS_ASSISTANT} tool with the recommendation for what action to take
3. Report the outcome

If the issue is resolved, respond with "No action needed."
Keep iterating until the issue is resolved or no further action is needed.
Maximum 5 iterations per log file.""",
            tools=devops_connected_tool.definitions + log_toolset.definitions,
        )
        logging.info(f"Orchestrator agent created: id={orchestrator_agent.id}")

        delay = 15
        max_iterations = 5

        # Process log files
        for filename in os.listdir(file_path):
            logfile_path = f"{file_path}/{filename}"
            
            logging.info(f"\nProcessing log file: {filename}")
            print(f"\nProcessing log file: {filename}\n")
            
            # Create a new thread for each log file
            logging.info("Creating a new thread for this log file...")
            thread = await client.agents.create_thread()
            logging.info(f"Thread created: id={thread.id}")
            
            try:
                iteration = 0
                resolved = False
                
                while iteration < max_iterations and not resolved:
                    iteration += 1
                    logging.info(f"Iteration {iteration}/{max_iterations}")
                    
                    # Create the prompt for this iteration
                    if iteration == 1:
                        prompt = f"Analyze this log file and take appropriate corrective action: {logfile_path}"
                    else:
                        prompt = f"Check if the issue in {logfile_path} has been resolved. If not, take further action."
                    
                    logging.debug(f"Prompt: {prompt}")
                    
                    # Create message
                    await client.agents.create_message(
                        thread_id=thread.id,
                        role="user",
                        content=prompt
                    )
                    logging.debug("User message created.")
                    
                    # Run the orchestrator
                    logging.info("Starting orchestrator run...")
                    run = await client.agents.create_and_process_run(
                        thread_id=thread.id,
                        agent_id=orchestrator_agent.id
                    )
                    logging.info(f"Run finished: id={run.id}, status={run.status}")
                    
                    if run.status == "failed":
                        error_msg = f"Run failed: {run.last_error}"
                        logging.error(error_msg)
                        print(error_msg)
                        if "Rate limit is exceeded" in str(run.last_error):
                            logging.warning("Waiting for rate limit...")
                            print("Waiting for rate limit...")
                            await asyncio.sleep(60)
                            continue
                        else:
                            break
                    
                    # Get the latest message
                    messages = await client.agents.list_messages(thread_id=thread.id)
                    last_msg = messages.get_last_text_message_by_role("assistant")
                    
                    if last_msg:
                        response_content = last_msg.text.value
                        logging.info(f"Iteration {iteration}: {response_content}")
                        print(f"Iteration {iteration}: {response_content}\n")
                        
                        # Check if resolved
                        if "no action needed" in response_content.lower():
                            resolved = True
                            outcome_msg = f"Issue in {filename} resolved."
                            logging.info(outcome_msg)
                            print(outcome_msg + "\n")
                    
                    await asyncio.sleep(delay)  # Wait to reduce TPM
                
                # Clean up thread
                logging.info("Deleting thread...")
                await client.agents.delete_thread(thread.id)
                logging.info("Thread deleted.")
                
            except Exception as e:
                error_msg = f"Error processing {filename}: {e}"
                logging.error(error_msg)
                print(error_msg)
                if "Rate limit is exceeded" in str(e):
                    logging.warning("Waiting...")
                    print("Waiting...")
                    await asyncio.sleep(60)
                continue

        # Clean up agents
        logging.info("Cleaning up agents...")
        await client.agents.delete_agent(orchestrator_agent.id)
        logging.info("Orchestrator agent deleted.")
        await client.agents.delete_agent(incident_agent.id)
        logging.info("Incident manager agent deleted.")
        await client.agents.delete_agent(devops_agent.id)
        logging.info("DevOps assistant agent deleted.")

# Start the app
if __name__ == "__main__":
    asyncio.run(main())