import os
import logging
import asyncio
from dotenv import load_dotenv
from azure.identity.aio import DefaultAzureCredential
from azure.ai.projects.aio import AIProjectClient
from azure.ai.projects.models import FunctionTool, ToolSet
from email_plugin import user_functions

# Import logging configuration
from log_util import LogUtil, vdebug

# Load environment variables early
load_dotenv()

# Read logging configuration from environment
verbose_output = os.getenv("VERBOSE_OUTPUT", "false") == "true"

# Setup logging with explicit parameters
logging_config = LogUtil()
logging_config.setup_logging(verbose=verbose_output)

async def main():
    logging.info("Starting expense claim submission...")

    # Create expense claim data
    data = """date,description,amount
              07-Mar-2025,taxi,24.00
              07-Mar-2025,dinner,65.50
              07-Mar-2025,hotel,125.90"""
    
    logging.info(f"Expense data prepared: {len(data.splitlines())} lines")

    # Run the async agent code
    await create_expense_claim(data)

async def create_expense_claim(expenses_data):

    # Get configuration settings
    project_endpoint = os.getenv("PROJECT_ENDPOINT")
    model_deployment = os.getenv("MODEL_DEPLOYMENT")
    
    if not project_endpoint or not model_deployment:
        logging.warning("Environment variables PROJECT_ENDPOINT or MODEL_DEPLOYMENT are missing.")
    else:
        logging.info(f"Using project endpoint: {project_endpoint}")
        logging.info(f"Using model deployment: {model_deployment}")

    # Connect to the Azure AI Foundry project
    logging.info("Initializing AIProjectClient...")
    async with (
        DefaultAzureCredential(
            exclude_environment_credential=True,
            exclude_managed_identity_credential=True) as creds,
        AIProjectClient(
            endpoint=project_endpoint,
            credential=creds
        ) as project_client,
    ):
        logging.info("AIProjectClient initialized.")
        
        # Create function tools from user functions
        logging.info("Creating function tools for email plugin...")
        functions = FunctionTool(user_functions)
        toolset = ToolSet()
        toolset.add(functions)
        logging.debug(f"Function tools created: {len(user_functions)} functions")
        
        # Define an Azure AI agent that sends an expense claim email
        logging.info("Creating expenses agent...")
        expenses_agent = await project_client.agents.create_agent(
            model=model_deployment,
            name="expenses_agent",
            instructions="""You are an AI assistant for expense claim submission.
                            When a user submits expenses data and requests an expense claim, use the plug-in function to send an email to expenses@contoso.com with the subject 'Expense Claim' and a body that contains itemized expenses with a total.
                            Then confirm to the user that you've done so.""",
            toolset=toolset
        )
        logging.info(f"Expenses agent created: id={expenses_agent.id}")

        # Create a thread for the conversation
        logging.info("Creating a new thread for the conversation...")
        thread = await project_client.agents.create_thread()
        logging.info(f"Thread created: id={thread.id}")
        
        try:
            # Add the input prompt as a message
            prompt = f"Create an expense claim for the following expenses: {expenses_data}"
            logging.info("Sending user message to thread...")
            await project_client.agents.create_message(
                thread_id=thread.id,
                role="user",
                content=prompt
            )
            logging.info("Message sent.")
            
            # Create and process the run
            logging.info("Starting run (create_and_process)...")
            run = await project_client.agents.create_and_process_run(
                thread_id=thread.id,
                agent_id=expenses_agent.id
            )
            logging.info(f"Run finished: id={run.id}, status={run.status}")
            
            # Check the run status
            if run.status == "failed":
                logging.error(f"Run failed: {run.last_error}")
            else:
                logging.info("Run succeeded. Collecting messages...")
                # Get the messages
                messages = await project_client.agents.list_messages(thread_id=thread.id)
                
                # Display the response
                last_msg = messages.get_last_text_message_by_role("assistant")
                if last_msg:
                    logging.info(f"\n# {expenses_agent.name}:\n{last_msg.text.value}")
                    print(f"\n# {expenses_agent.name}:\n{last_msg.text.value}")
                    
        except Exception as e:
            # Something went wrong
            logging.error(f"Error during execution: {e}")
        finally:
            # Cleanup: Delete the thread and agent
            logging.info("Cleaning up agents and thread...")
            if thread:
                await project_client.agents.delete_thread(thread.id)
                logging.info("Thread deleted.")
            await project_client.agents.delete_agent(expenses_agent.id)
            logging.info("Agent deleted.")


if __name__ == "__main__":
    asyncio.run(main())
