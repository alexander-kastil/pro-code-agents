"""
Azure AI Agents with Bing Grounding Demo

This demo shows how to use Bing Search with Azure AI Agents Service.
Note: HostedWebSearchTool is NOT supported with AzureOpenAIChatClient.
For web search, you must use Azure AI Agents Service with BingGroundingTool.

Requirements:
- Azure AI Foundry Project
- Bing Search connection configured in your project
"""

import os
import logging
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential

from azure.ai.projects import AIProjectClient
from azure.ai.agents.models import BingGroundingTool

from utils.log_util import LogUtil, vdebug

# Load environment variables
load_dotenv()

PROJECT_ENDPOINT = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
MODEL_DEPLOYMENT = os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME")


def main():
    """Interactive demo: Azure AI Agent with Bing Grounding for web search."""
    
    # Setup logging (use verbose=True to see debug logs including tool calls)
    log_util = LogUtil()
    log_util.setup_logging(verbose=True)
    
    print("\n" + "="*70)
    print("🌐 DEMO: Azure AI Agents - Bing Grounding (Web Search)")
    print("="*70)
    print("""
This demo uses Azure AI Agents Service with Bing Grounding for web search.

KEY DIFFERENCES from HostedWebSearchTool:
- Uses Azure AI Agents Service (not ChatCompletion API)
- Requires Azure AI Foundry Project
- Uses BingGroundingTool (not HostedWebSearchTool)
- Properly supports web search functionality

Examples to try:
- "Search for the latest news about AI agents"
- "What is the current weather in Seattle?"
- "Find recent news about Equinox Gold"
- "What are the latest developments in quantum computing?"
    """)
    
    try:
        # Create Azure AI Project client
        credential = DefaultAzureCredential()
        project_client = AIProjectClient(
            endpoint=PROJECT_ENDPOINT,
            credential=credential
        )
        
        logging.info(f"Connected to Azure AI Project: {PROJECT_ENDPOINT}")
        
        # Create Bing Grounding tool
        # Note: BingGroundingTool requires a connection_id for the Bing resource
        # You need to create a Bing connection in your Azure AI Foundry project first
        # For now, we'll use a placeholder - you need to replace this with your actual connection ID
        # Get it from Azure AI Foundry portal under Settings > Connections
        
        # Option 1: Use environment variable for connection ID
        bing_connection_id = os.getenv("BING_CONNECTION_ID")
        
        if not bing_connection_id:
            print("\n❌ Error: BING_CONNECTION_ID not found in environment variables")
            print("\nTo use Bing Grounding, you need to:")
            print("1. Create a Bing Search connection in Azure AI Foundry portal")
            print("2. Add BING_CONNECTION_ID to your .env file")
            print("3. The connection ID format is typically:")
            print("   /subscriptions/<sub-id>/resourceGroups/<rg>/providers/Microsoft.MachineLearningServices/")
            print("   workspaces/<project>/connections/<connection-name>")
            return
        
        bing_tool = BingGroundingTool(connection_id=bing_connection_id)
        logging.info(f"Using Bing connection: {bing_connection_id}")
        
        # Create agent with Bing Search - using context manager
        with project_client:
            agent = project_client.agents.create_agent(
                model=MODEL_DEPLOYMENT,
                name="BingSearchBot",
                instructions=(
                    "You are a helpful assistant with access to web search via Bing. "
                    "Use web search to find current information, news, and real-time data. "
                    "Always cite your sources and provide accurate, up-to-date information."
                ),
                tools=bing_tool.definitions,
                tool_resources=bing_tool.resources
            )
            
            logging.info(f"Created agent: {agent.id}")
            print("\n✅ Agent created with Bing Grounding")
            print(f"   Agent ID: {agent.id}")
            print(f"   Model: {MODEL_DEPLOYMENT}")
            
            print("\n" + "="*70)
            print("💬 Interactive Chat (Type 'quit' to exit)")
            print("="*70 + "\n")
            
            # Create a thread for conversation
            thread = project_client.agents.create_thread()
            logging.info(f"Created thread: {thread.id}")
            
            while True:
                try:
                    user_input = input("You: ")
                except (EOFError, KeyboardInterrupt):
                    print("\n👋 Exiting...")
                    break
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("\n👋 Goodbye!")
                    break
                
                if not user_input.strip():
                    continue
                
                logging.info(f"User query: {user_input}")
                
                # Add message to thread
                project_client.agents.create_message(
                    thread_id=thread.id,
                    role="user",
                    content=user_input
                )
                
                # Run the agent
                run = project_client.agents.create_and_process_run(
                    thread_id=thread.id,
                    agent_id=agent.id
                )
                
                logging.info(f"Run completed with status: {run.status}")
                
                # Log tool calls if any
                if hasattr(run, 'required_action') and run.required_action:
                    vdebug(f"Tool calls: {run.required_action}")
                
                # Get messages
                messages = project_client.agents.list_messages(thread_id=thread.id)
                
                # Print assistant's response (get the latest message)
                print("Agent: ", end="", flush=True)
                if messages.data:
                    # Messages are in reverse chronological order, so get first one
                    latest_message = messages.data[0]
                    if latest_message.role == "assistant":
                        for content in latest_message.content:
                            if hasattr(content, 'text') and content.text:
                                print(content.text.value)
                print()
            
            # Cleanup
            logging.info("Cleaning up resources...")
            project_client.agents.delete_agent(agent.id)
            logging.info(f"Deleted agent: {agent.id}")
        
    except Exception as e:
        logging.error(f"Error: {e}")
        print(f"\n❌ Error: {e}")
        print("\nPlease ensure you have:")
        print("1. Azure AI Foundry Project configured")
        print("2. Bing Search connection set up in your project")
        print("3. AZURE_AI_PROJECT_ENDPOINT in your .env file")
        raise


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 See you again soon.")
