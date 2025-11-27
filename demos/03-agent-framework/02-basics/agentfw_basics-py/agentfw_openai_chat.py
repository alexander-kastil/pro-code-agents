import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition

# Load environment variables
load_dotenv()

endpoint = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
model = os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME", "gpt-4o")
delete_resources = os.getenv("DELETE", "true").lower() == "true"


def main():
    """Interactive demo: Azure OpenAI direct chat using Foundry Responses API."""
    
    print("\n" + "="*70)
    print("DEMO: Direct Azure OpenAI Chat (Foundry Responses API)")
    print("="*70)
    
    # Initialize project client and OpenAI responses client
    project_client = AIProjectClient(endpoint=endpoint, credential=DefaultAzureCredential())
    openai_client = project_client.get_openai_client()
    
    with project_client:
        # Create versioned agent (prompt kind)
        agent = project_client.agents.create_version(
            agent_name="direct-chat-bot",
            definition=PromptAgentDefinition(
                model=model,
                instructions="You are a helpful assistant. Be concise and clear."
            )
        )
        
        print(f"\nAgent created: {agent.name} (version {agent.version})")
        
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
        
        # Cleanup based on DELETE flag
        if delete_resources:
            project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
            print("Deleted agent version")
        else:
            print(f"Agent preserved: {agent.name}:{agent.version}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nSee you again soon.")
