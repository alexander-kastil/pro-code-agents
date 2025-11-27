"""
Expense Claim Submission Agent using Microsoft Agent Framework with Foundry Responses API

This agent demonstrates:
- Microsoft Foundry (formerly Azure AI Foundry) integration with Agent Framework
- Persistent agent creation using agent_name parameter
- Responses API for efficient, stateful conversation handling
- Automatic agent lifecycle management (create/reuse versioned agents)

Migration notes:
- Changed import: from agent_framework.azure -> from agent_framework_azure_ai
- Added agent_name parameter to AzureAIAgentClient for Foundry persistence
- Removed name parameter from ChatAgent (agent_name in client handles this)
"""

import os
import logging
import asyncio
from dotenv import load_dotenv
from azure.identity.aio import DefaultAzureCredential
from agent_framework import ChatAgent
from agent_framework_azure_ai import AzureAIAgentClient
from email_plugin import user_functions

# Import logging configuration
from log_util import LogUtil

# Import diagram generator
from diagram_generator import MermaidDiagramGenerator

# Load environment variables early
load_dotenv()

# Read logging configuration from environment
verbose_output = os.getenv("VERBOSE_OUTPUT", "false") == "true"
create_mermaid_diagram = os.getenv("CREATE_MERMAID_DIAGRAM", "false") == "true"
output_folder = os.getenv("OUTPUT_PATH", "./output")
data_folder = os.getenv("DATA_PATH", "./data")

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
        logging.error(
            "Missing required environment variables PROJECT_ENDPOINT or MODEL_DEPLOYMENT. "
            "Set them in your .env file before running."
        )
        return

    logging.info(f"Using project endpoint: {project_endpoint}")
    logging.info(f"Using model deployment: {model_deployment}")

    # Create the Azure AI agent using Microsoft Agent Framework with Foundry
    logging.info("Initializing Azure AI Agent with Agent Framework (Foundry Responses API)...")
    credential = DefaultAzureCredential(
        exclude_environment_credential=True,
        exclude_managed_identity_credential=True
    )
    
    # Create agent with persistent agent in Foundry
    # The agent_name parameter creates/reuses a versioned agent in Microsoft Foundry
    agent = ChatAgent(
        chat_client=AzureAIAgentClient(
            project_endpoint=project_endpoint,
            model_deployment_name=model_deployment,
            async_credential=credential,
            agent_name="expenses_agent"  # Creates persistent agent in Foundry
        ),
        instructions="""You are an AI assistant for expense claim submission.
                        When a user submits expenses data and requests an expense claim, summarize the expenses with an itemized list and a total.
                        Then respond confirming the formatted claim.""",
    )
    
    async with credential:
        async with agent:
            logging.info("Agent created successfully.")
            
            try:
                # Create the prompt
                prompt = f"Create an expense claim for the following expenses: {expenses_data}"
                logging.info("Sending message to agent...")
                
                # Run the agent
                result = await agent.run(prompt)
                
                logging.info("Agent response received.")
                resolution = result.text
                logging.info(f"\n# Expense Agent:\n{resolution}")
                print(f"\n# Expense Agent:\n{resolution}")
                
                # Extract token usage if available
                token_usage_in = 0
                token_usage_out = 0
                if hasattr(result, 'usage') and result.usage:
                    token_usage_in = getattr(result.usage, 'input_tokens', 0)
                    token_usage_out = getattr(result.usage, 'output_tokens', 0)
                    logging.debug(f"Token usage - Input: {token_usage_in}, Output: {token_usage_out}")
                
                # Generate diagram if enabled
                if create_mermaid_diagram:
                    logging.info("Generating Mermaid diagram ...")
                    diagram_generator = MermaidDiagramGenerator(ticket_folder_path=output_folder)
                    diagram_generator.save_diagram_file(
                        ticket_prompt=prompt,
                        resolution=resolution,
                        token_usage_in=token_usage_in,
                        token_usage_out=token_usage_out
                    )
                        
            except Exception as e:
                # Something went wrong
                logging.error(f"Error during execution: {e}")


if __name__ == "__main__":
    asyncio.run(main())
