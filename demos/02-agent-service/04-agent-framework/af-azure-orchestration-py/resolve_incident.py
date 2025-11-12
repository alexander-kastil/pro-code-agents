import os
from dotenv import load_dotenv
from datetime import datetime
from pathlib import Path
import shutil

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.agents.models import FunctionTool, ToolSet
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

def main():
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
    model_deployment = os.getenv("MODEL_DEPLOYMENT")

    # Connect to the Azure AI Foundry project
    project_client = AIProjectClient(
        endpoint=project_endpoint,
        credential=DefaultAzureCredential()
    )
    
    with project_client:
        # Create function tools for log reading
        log_tool = FunctionTool(log_functions)
        log_toolset = ToolSet()
        log_toolset.add(log_tool)
        
        # Create the incident manager agent on the Azure AI agent service
        incident_agent = project_client.agents.create_agent(
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
        devops_agent = project_client.agents.create_agent(
            model=model_deployment,
            name=DEVOPS_ASSISTANT,
            instructions=DEVOPS_ASSISTANT_INSTRUCTIONS,
            toolset=devops_toolset
        )

        delay = 15
        max_iterations = 5

        # Process log files
        for filename in os.listdir(file_path):
            logfile_path = f"{file_path}/{filename}"
            
            print(f"\nProcessing log file: {filename}\n")
            
            # Create a new thread for each log file
            thread = project_client.agents.threads.create()
            
            try:
                iteration = 0
                resolved = False
                
                while iteration < max_iterations and not resolved:
                    iteration += 1
                    
                    # Create the prompt for this iteration
                    if iteration == 1:
                        prompt = f"Analyze this log file and recommend corrective action: {logfile_path}"
                    else:
                        prompt = f"Re-read the log file {logfile_path} to verify if the previous issue has been resolved. If the error is gone, respond with 'No action needed'. If the error still exists or a new error appeared, recommend the appropriate corrective action."
                    
                    # Create message
                    project_client.agents.create_message(
                        thread_id=thread.id,
                        role="user",
                        content=prompt
                    )
                    
                    # Run the incident manager
                    incident_run = project_client.agents.create_and_process_run(
                        thread_id=thread.id,
                        agent_id=incident_agent.id
                    )
                    
                    if incident_run.status == "failed":
                        print(f"Incident manager run failed: {incident_run.last_error}")
                        if incident_run.last_error and "rate_limit_exceeded" in str(incident_run.last_error):
                            print("Waiting for rate limit...")
                            import time
                            time.sleep(60)
                            continue
                        else:
                            break
                    
                    # Get the incident manager recommendation
                    messages = project_client.agents.list_messages(thread_id=thread.id)
                    last_msg = messages.get_last_text_message_by_role("assistant")
                    
                    if last_msg:
                        recommendation = last_msg.text.value
                        print(f"Iteration {iteration} - Incident Manager: {recommendation}\n")
                        
                        # Check if resolved or escalated
                        if "no action needed" in recommendation.lower():
                            resolved = True
                            print(f"Issue in {filename} resolved.\n")
                            break
                        
                        if "escalate issue" in recommendation.lower():
                            resolved = True
                            print(f"Issue in {filename} escalated to higher support tier.\n")
                            # Still execute the escalation action
                        
                        # Create a message for the devops agent
                        project_client.agents.create_message(
                            thread_id=thread.id,
                            role="user",
                            content=recommendation
                        )
                        
                        # Run the devops agent
                        devops_run = project_client.agents.create_and_process_run(
                            thread_id=thread.id,
                            agent_id=devops_agent.id
                        )
                        
                        if devops_run.status == "failed":
                            print(f"DevOps agent run failed: {devops_run.last_error}")
                            break
                        
                        # Get the devops agent response
                        devops_messages = project_client.agents.list_messages(thread_id=thread.id)
                        devops_msg = devops_messages.get_last_text_message_by_role("assistant")
                        
                        if devops_msg:
                            print(f"Iteration {iteration} - DevOps Assistant: {devops_msg.text.value}\n")
                    
                    import time
                    time.sleep(delay)  # Wait to reduce TPM
                
                # Clean up thread
                project_client.agents.delete_thread(thread.id)
                
            except Exception as e:
                print(f"Error processing {filename}: {e}")
                if "Rate limit is exceeded" in str(e):
                    print("Waiting...")
                    import time
                    time.sleep(60)
                continue

        # Clean up agents
        project_client.agents.delete_agent(incident_agent.id)
        project_client.agents.delete_agent(devops_agent.id)

# Start the app
if __name__ == "__main__":
    main()