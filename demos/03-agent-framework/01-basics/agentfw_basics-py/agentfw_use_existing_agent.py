"""
NEW 02: Use Existing Azure AI Foundry Agent (Interactive Demo)

This demo connects to an EXISTING agent in Azure AI Foundry.
You'll need to update the .env02 file with your agent ID.
"""

import asyncio
import os
import logging
from dotenv import load_dotenv

from agent_framework import ChatAgent
from agent_framework.azure import AzureAIAgentClient
from azure.identity.aio import AzureCliCredential

# Import logging configuration
from log_util import LogUtil, vdebug

# Import diagram generator
from diagram_generator import MermaidDiagramGenerator

# Load environment variables early
load_dotenv('.env02')

# Read logging configuration from environment
verbose_output = os.getenv("VERBOSE_OUTPUT", "false") == "true"
create_mermaid_diagram = os.getenv("CREATE_MERMAID_DIAGRAM", "false") == "true"
output_folder = os.getenv("OUTPUT_PATH", "./output")
data_folder = os.getenv("DATA_PATH", "./data")

# Setup logging with explicit parameters
logging_config = LogUtil()
logging_config.setup_logging(verbose=verbose_output)

PROJECT_ENDPOINT = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
AGENT_ID = os.getenv("AZURE_AI_AGENT_ID")


async def main():
    """Interactive demo: Connect to existing agent."""
    
    print("\n" + "="*70)
    print("🔗 DEMO: Connect to Existing Azure AI Foundry Agent")
    print("="*70)
    
    print(f"\n📋 Connecting to agent: {AGENT_ID}")
    
    async with (
        AzureCliCredential() as credential,
        ChatAgent(
            chat_client=AzureAIAgentClient(
                async_credential=credential,
                project_endpoint=PROJECT_ENDPOINT,
                agent_id=AGENT_ID
            )
        ) as agent
    ):
        print("✅ Connected successfully!")
        
        print("\n" + "="*70)
        print("💬 Interactive Chat (Type 'quit' to exit)")
        print("="*70 + "\n")
        
        while True:
            # Get user input
            user_input = input("You: ")
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!")
                break
            
            if not user_input.strip():
                continue
            
            # Get streaming response
            print("Agent: ", end="", flush=True)
            async for chunk in agent.run_stream(user_input):
                if chunk.text:
                    print(chunk.text, end="", flush=True)
            print("\n")


if __name__ == "__main__":
    asyncio.run(main())
