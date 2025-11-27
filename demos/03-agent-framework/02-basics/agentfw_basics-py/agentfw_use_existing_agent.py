import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

# Load environment variables
load_dotenv()

endpoint = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
agent_name = os.getenv("AZURE_AI_AGENT_NAME", "")
agent_version = os.getenv("AZURE_AI_AGENT_VERSION", "")


def main():
    """Interactive demo: Connect to existing agent using Foundry Responses API."""
    
    print("\n" + "="*70)
    print("DEMO: Connect to Existing Azure AI Foundry Agent")
    print("="*70)
    
    if not agent_name or not agent_version:
        print("\nError: AZURE_AI_AGENT_NAME and AZURE_AI_AGENT_VERSION must be set in .env")
        print("Set these to an existing agent's name and version to connect.")
        return
    
    print(f"\nConnecting to agent: {agent_name} (version {agent_version})")
    
    # Initialize project client and OpenAI responses client
    project_client = AIProjectClient(endpoint=endpoint, credential=DefaultAzureCredential())
    openai_client = project_client.get_openai_client()
    
    with project_client:
        # Verify agent exists
        agent = project_client.agents.get_version(agent_name=agent_name, agent_version=agent_version)
        print(f"Connected to agent: {agent.name} (version {agent.version})")
        
        print("\n" + "="*70)
        print("Interactive Chat (Type 'quit' to exit)")
        print("="*70 + "\n")
        
        # Conversation history for multi-turn support
        conversation_history = []
        
        while True:
            # Get user input
            try:
                user_input = input("You: ")
            except EOFError:
                print("\nReceived EOF - exiting.")
                break
            except KeyboardInterrupt:
                print("\nInterrupted - exiting.")
                break
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\nGoodbye!")
                break
            
            if not user_input.strip():
                continue
            
            # Add user message to history
            conversation_history.append({"role": "user", "content": user_input})
            
            # Create response using Foundry Responses API
            response = openai_client.responses.create(
                input=conversation_history,
                extra_body={"agent": {"type": "agent_reference", "name": agent.name, "version": agent.version}}
            )
            
            # Process response
            if response.status == "completed":
                for item in response.output:
                    if item.type == "message" and item.content and item.content[0].type == "output_text":
                        assistant_text = item.content[0].text
                        print(f"Agent: {assistant_text}\n")
                        # Add assistant response to history for multi-turn
                        conversation_history.append({"role": "assistant", "content": assistant_text})
            else:
                print(f"Response failed: {response.status}")
                if response.error:
                    print(f"Error: {response.error}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nSee you again soon.")
