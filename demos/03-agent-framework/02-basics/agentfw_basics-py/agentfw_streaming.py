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
    """Interactive demo: Create agent and demonstrate streaming responses."""
    
    print("\n" + "="*70)
    print("DEMO: Response Streaming with Foundry Responses API")
    print("="*70)
    
    # Initialize project client and OpenAI responses client
    project_client = AIProjectClient(endpoint=endpoint, credential=DefaultAzureCredential())
    openai_client = project_client.get_openai_client()
    
    with project_client:
        print("\nCreating new agent in Azure AI Foundry...")
        
        # Create versioned agent (prompt kind)
        agent = project_client.agents.create_version(
            agent_name="streaming-demo-agent",
            definition=PromptAgentDefinition(
                model=model,
                instructions=(
                    "You are a helpful AI assistant that provides detailed, "
                    "informative responses. Be thorough and engaging in your explanations."
                )
            )
        )
        
        print(f"Agent created successfully!")
        print(f"   Agent Name: {agent.name}")
        print(f"   Version: {agent.version}")
        
        print("\n" + "="*70)
        print("Interactive Streaming Chat")
        print("="*70)
        print("\nTIP: Responses will stream in real-time, token by token")
        print("TIP: Try asking for longer responses to see streaming in action")
        print("Examples:")
        print("   - 'Explain how neural networks work'")
        print("   - 'Tell me a creative story about a robot'")
        print("   - 'Describe the process of photosynthesis'")
        print("\n" + "="*70)
        print("Type 'quit' to exit\n")
        
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
            
            # Get streaming response using Foundry Responses API
            print("\nAgent: ", end="", flush=True)
            
            # Use streaming mode
            with openai_client.responses.create(
                input=conversation_history,
                extra_body={"agent": {"type": "agent_reference", "name": agent.name, "version": agent.version}},
                stream=True
            ) as stream:
                full_response = ""
                for event in stream:
                    if hasattr(event, 'type'):
                        if event.type == "response.output_text.delta":
                            print(event.delta, end="", flush=True)
                            full_response += event.delta
                        elif event.type == "response.completed":
                            # Response completed
                            pass
            
            print("\n")
            
            # Add assistant response to history for multi-turn
            if full_response:
                conversation_history.append({"role": "assistant", "content": full_response})
        
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
    except Exception as e:
        print(f"\nUnexpected error: {e}")
