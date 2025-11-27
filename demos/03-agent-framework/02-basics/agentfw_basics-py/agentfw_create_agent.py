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
    """Interactive demo: Create agent and chat using Foundry Responses API."""
    
    print("\n" + "="*70)
    print("DEMO: Create Azure AI Foundry Agent (Interactive)")
    print("="*70)
    
    # Initialize project client with DefaultAzureCredential
    # Note: Ensure you're logged in via Azure CLI: az login
    credential = DefaultAzureCredential(
        exclude_environment_credential=True,
        exclude_managed_identity_credential=True
    )
    
    with (
        credential,
        AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
        project_client.get_openai_client() as openai_client
    ):
        print("\nCreating new agent in Azure AI Foundry...")
        
        # Create versioned agent (prompt kind)
        agent = project_client.agents.create_version(
            agent_name="afw-first-agent",
            definition=PromptAgentDefinition(
                model=model,
                instructions="You are a helpful AI assistant. Be concise and friendly."
            )
        )
        
        print(f"Agent created successfully!")
        print(f"   Agent Name: {agent.name}")
        print(f"   Agent Version: {agent.version}")
        
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
    except Exception as e:
        error_msg = str(e)
        print(f"\nUnexpected error: {e}")
        
        # Provide helpful guidance for authentication errors
        if "401" in error_msg or "Unauthorized" in error_msg:
            print("\n" + "="*70)
            print("Authentication Error - Please check:")
            print("="*70)
            print("1. Ensure you're logged in to Azure CLI:")
            print("   Run: az login")
            print("\n2. Verify you have access to the Azure AI Foundry project")
            print("\n3. Check that your account has the required roles:")
            print("   - Azure AI Developer or Cognitive Services OpenAI User")
            print("="*70)
