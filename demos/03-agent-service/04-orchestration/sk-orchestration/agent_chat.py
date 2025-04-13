import asyncio
import os
from dotenv import load_dotenv
from datetime import datetime
from pathlib import Path
import shutil

from azure.identity.aio import DefaultAzureCredential
from semantic_kernel.agents import AgentGroupChat
from semantic_kernel.agents import AzureAIAgent, AzureAIAgentSettings
from semantic_kernel.contents.chat_message_content import ChatMessageContent
from semantic_kernel.contents.utils.author_role import AuthorRole
from semantic_kernel.functions.kernel_function_decorator import kernel_function
from log_plugin import LogFilePlugin
from strategies import SelectionStrategy, ApprovalTerminationStrategy
from devops_plugin import DevopsPlugin

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
    ai_agent_settings = AzureAIAgentSettings.create()


    async with (
       DefaultAzureCredential(
         exclude_environment_credential=True,
         exclude_managed_identity_credential=True) as creds,
        AzureAIAgent.create_client(
         credential=creds
     ) as client,
    ):
    
        # Create the incident manager agent on the Azure AI agent service
        incident_agent_definition = await client.agents.create_agent(
            model=ai_agent_settings.model_deployment_name,
            name=INCIDENT_MANAGER,
            instructions=INCIDENT_MANAGER_INSTRUCTIONS
        )

        # Create a Semantic Kernel agent for the Azure AI incident manager agent
        agent_incident = AzureAIAgent(
            client=client,
            definition=incident_agent_definition,
            plugins=[LogFilePlugin()]
        )

        # Create the devops agent on the Azure AI agent service
        devops_agent_definition = await client.agents.create_agent(
            model=ai_agent_settings.model_deployment_name,
            name=DEVOPS_ASSISTANT,
            instructions=DEVOPS_ASSISTANT_INSTRUCTIONS,
        )

        # Create a Semantic Kernel agent for the devops Azure AI agent
        agent_devops = AzureAIAgent(
            client=client,
            definition=devops_agent_definition,
            plugins=[DevopsPlugin()]
        )

        # Add the agents to a group chat with a custom termination and selection strategy
        chat = AgentGroupChat(
            agents=[agent_incident, agent_devops],
            termination_strategy=ApprovalTerminationStrategy(
                agents=[agent_incident], 
                maximum_iterations=5, 
                automatic_reset=True
            ),
            selection_strategy=SelectionStrategy(agents=[agent_incident,agent_devops]),      
        )        

        delay = 15

         # Process log files
        for filename in os.listdir(file_path):
            logfile_msg = ChatMessageContent(role=AuthorRole.USER, content=f"USER > {file_path}/{filename}")
            
            print(f"\nReady to process log file: {filename}\n")
            # Append the current log file to the chat
            await chat.add_chat_message(logfile_msg)
            print()

            try:
                print()

                # Invoke a response from the agents
                async for response in chat.invoke():
                    if response is None or not response.name:
                        continue
                    print(f"{response.content}")
                await asyncio.sleep(delay) # Wait to reduce TPM
            except Exception as e:
                print(f"Error during chat invocation: {e}")
                # If TPM rate exceeded, wait 60 secs
                if "Rate limit is exceeded" in str(e):
                    print ("Waiting...")
                    await asyncio.sleep(60)
                    continue
                else:
                    break

# Start the app
if __name__ == "__main__":
    asyncio.run(main())