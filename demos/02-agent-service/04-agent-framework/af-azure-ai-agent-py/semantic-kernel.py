import os
import asyncio
from dotenv import load_dotenv
from azure.identity.aio import DefaultAzureCredential
from azure.ai.projects.aio import AIProjectClient
from azure.ai.projects.models import FunctionTool, ToolSet
from email_plugin import user_functions

async def main():
    # Clear the console
    os.system('cls' if os.name=='nt' else 'clear')

    # Create expense claim data
    data = """date,description,amount
              07-Mar-2025,taxi,24.00
              07-Mar-2025,dinner,65.50
              07-Mar-2025,hotel,125.90"""

    # Run the async agent code
    await create_expense_claim(data)

async def create_expense_claim(expenses_data):

    # Get configuration settings
    load_dotenv()
    project_endpoint = os.getenv("PROJECT_ENDPOINT")
    model_deployment = os.getenv("MODEL_DEPLOYMENT_NAME")

    # Connect to the Azure AI Foundry project
    async with (
        DefaultAzureCredential(
            exclude_environment_credential=True,
            exclude_managed_identity_credential=True) as creds,
        AIProjectClient(
            endpoint=project_endpoint,
            credential=creds
        ) as project_client,
    ):
        
        # Create function tools from user functions
        functions = FunctionTool(user_functions)
        toolset = ToolSet()
        toolset.add(functions)
        
        # Define an Azure AI agent that sends an expense claim email
        expenses_agent = await project_client.agents.create_agent(
            model=model_deployment,
            name="expenses_agent",
            instructions="""You are an AI assistant for expense claim submission.
                            When a user submits expenses data and requests an expense claim, use the plug-in function to send an email to expenses@contoso.com with the subject 'Expense Claim' and a body that contains itemized expenses with a total.
                            Then confirm to the user that you've done so.""",
            toolset=toolset
        )

        # Create a thread for the conversation
        thread = await project_client.agents.create_thread()
        
        try:
            # Add the input prompt as a message
            prompt = f"Create an expense claim for the following expenses: {expenses_data}"
            await project_client.agents.create_message(
                thread_id=thread.id,
                role="user",
                content=prompt
            )
            
            # Create and process the run
            run = await project_client.agents.create_and_process_run(
                thread_id=thread.id,
                agent_id=expenses_agent.id
            )
            
            # Check the run status
            if run.status == "failed":
                print(f"Run failed: {run.last_error}")
            else:
                # Get the messages
                messages = await project_client.agents.list_messages(thread_id=thread.id)
                
                # Display the response
                last_msg = messages.get_last_text_message_by_role("assistant")
                if last_msg:
                    print(f"\n# {expenses_agent.name}:\n{last_msg.text.value}")
                    
        except Exception as e:
            # Something went wrong
            print(e)
        finally:
            # Cleanup: Delete the thread and agent
            if thread:
                await project_client.agents.delete_thread(thread.id)
            await project_client.agents.delete_agent(expenses_agent.id)


if __name__ == "__main__":
    asyncio.run(main())
