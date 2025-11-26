import asyncio
import os
from dotenv import load_dotenv

from agent_framework.azure import AzureAIAgentClient
from azure.identity.aio import AzureCliCredential

# Load environment variables
load_dotenv()

PROJECT_ENDPOINT = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
MODEL_DEPLOYMENT = os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME")


async def main():
    """Interactive demo: Create agent and chat using Microsoft Agent Framework."""
    
    print("\n" + "="*70)
    print("DEMO: Create Azure AI Foundry Agent (Interactive)")
    print("="*70)
    
    async with AzureCliCredential() as credential:
        # Create agent using AzureAIAgentClient
        # This creates a ChatAgent with AzureAIAgentClient configured
        print("\nCreating new agent in Azure AI Foundry...")
        
        async with AzureAIAgentClient(
            project_endpoint=PROJECT_ENDPOINT,
            model_deployment_name=MODEL_DEPLOYMENT,
            async_credential=credential,
            should_cleanup_agent=True
        ).create_agent(
            name="First AFW Agent",
            instructions="You are a helpful AI assistant. Be concise and friendly."
        ) as agent:
            
            print(f"Agent created successfully!")
            print(f"   Agent Name: {agent.name}")
            
            print("\n" + "="*70)
            print("Interactive Chat (Type 'quit' to exit)")
            print("="*70 + "\n")
            
            while True:
                # Get user input
                try:
                    user_input = input("You: ")
                except EOFError:
                    print("\nReceived EOF - exiting.")
                    break
                except KeyboardInterrupt:
                    print("\n\nInterrupted - exiting.")
                    break
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("\nGoodbye!")
                    break
                
                if not user_input.strip():
                    continue
                
                # Get response from agent
                try:
                    print("Agent: ", end="", flush=True)
                    async for chunk in agent.run_stream(user_input):
                        if chunk.text:
                            print(chunk.text, end="", flush=True)
                    print("\n")
                except KeyboardInterrupt:
                    print("\n\nResponse interrupted - continuing chat.")
                    print()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nSee you again soon.")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
