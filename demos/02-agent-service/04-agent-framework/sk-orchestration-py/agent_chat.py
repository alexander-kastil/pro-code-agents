import asyncio
import os
from dotenv import load_dotenv
from datetime import datetime
from pathlib import Path
import shutil

from azure.identity.aio import DefaultAzureCredential
from azure.ai.projects.aio import AIProjectClient
from azure.ai.projects.models import FunctionTool, ToolSet, ConnectedAgentTool
from log_plugin import log_functions
from devops_plugin import devops_functions

INCIDENT_MANAGER = "INCIDENT_MANAGER"
INCIDENT_MANAGER_INSTRUCTIONS = """
Analyze the given log file or the response from the devops assistant.
Recommend which one of the following actions should be taken:

Restart service {service_name}
Rollback transaction
Redeploy resource {resource_name}
Increase quota

If there are no issues or if the issue has already been resolved, respond with "INCIDENT_MANAGER > No action needed."
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
    # Clear the console
    os.system('cls' if os.name=='nt' else 'clear')

    # Get the log files
    print("Getting log files...\n")
    script_dir = Path(__file__).parent  # Get the directory of the script
    src_path = script_dir / "sample_logs"
    file_path = script_dir / "logs"
    shutil.copytree(src_path, file_path, dirs_exist_ok=True)

    # Read the model deployment name from the environment variable
    load_dotenv()
    project_endpoint = os.getenv("PROJECT_ENDPOINT")
    model_deployment = os.getenv("MODEL_DEPLOYMENT_NAME")

    async with (
        DefaultAzureCredential(
            exclude_environment_credential=True,
            exclude_managed_identity_credential=True) as creds,
        AIProjectClient(
            endpoint=project_endpoint,
            credential=creds
        ) as client,
    ):
        # Create function tools for log reading
        log_tool = FunctionTool(log_functions)
        log_toolset = ToolSet()
        log_toolset.add(log_tool)
        
        # Create the incident manager agent on the Azure AI agent service
        incident_agent = await client.agents.create_agent(
            model=model_deployment,
            name=INCIDENT_MANAGER,
            instructions=INCIDENT_MANAGER_INSTRUCTIONS,
            toolset=log_toolset
        )

        # Create function tools for devops operations
        devops_tool = FunctionTool(devops_functions)
        devops_toolset = ToolSet()
        devops_toolset.add(devops_tool)
        
        # Create the devops agent on the Azure AI agent service
        devops_agent = await client.agents.create_agent(
            model=model_deployment,
            name=DEVOPS_ASSISTANT,
            instructions=DEVOPS_ASSISTANT_INSTRUCTIONS,
            toolset=devops_toolset
        )

        # Create a connected agent tool for the devops assistant
        devops_connected_tool = ConnectedAgentTool(
            id=devops_agent.id,
            name=DEVOPS_ASSISTANT,
            description="Performs devops operations like restart service, rollback transaction, redeploy resource, increase quota, or escalate issue"
        )
        
        # Create orchestrator agent that coordinates the two agents
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

        delay = 15
        max_iterations = 5

        # Process log files
        for filename in os.listdir(file_path):
            logfile_path = f"{file_path}/{filename}"
            
            print(f"\nProcessing log file: {filename}\n")
            
            # Create a new thread for each log file
            thread = await client.agents.create_thread()
            
            try:
                iteration = 0
                resolved = False
                
                while iteration < max_iterations and not resolved:
                    iteration += 1
                    
                    # Create the prompt for this iteration
                    if iteration == 1:
                        prompt = f"Analyze this log file and take appropriate corrective action: {logfile_path}"
                    else:
                        prompt = f"Check if the issue in {logfile_path} has been resolved. If not, take further action."
                    
                    # Create message
                    await client.agents.create_message(
                        thread_id=thread.id,
                        role="user",
                        content=prompt
                    )
                    
                    # Run the orchestrator
                    run = await client.agents.create_and_process_run(
                        thread_id=thread.id,
                        agent_id=orchestrator_agent.id
                    )
                    
                    if run.status == "failed":
                        print(f"Run failed: {run.last_error}")
                        if "Rate limit is exceeded" in str(run.last_error):
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
                        print(f"Iteration {iteration}: {response_content}\n")
                        
                        # Check if resolved
                        if "no action needed" in response_content.lower():
                            resolved = True
                            print(f"Issue in {filename} resolved.\n")
                    
                    await asyncio.sleep(delay)  # Wait to reduce TPM
                
                # Clean up thread
                await client.agents.delete_thread(thread.id)
                
            except Exception as e:
                print(f"Error processing {filename}: {e}")
                if "Rate limit is exceeded" in str(e):
                    print("Waiting...")
                    await asyncio.sleep(60)
                continue

        # Clean up agents
        await client.agents.delete_agent(orchestrator_agent.id)
        await client.agents.delete_agent(incident_agent.id)
        await client.agents.delete_agent(devops_agent.id)

# Start the app
if __name__ == "__main__":
    asyncio.run(main())