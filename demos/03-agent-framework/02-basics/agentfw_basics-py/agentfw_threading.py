import os
import json
from datetime import datetime
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition

# Load environment variables
load_dotenv('.env')

endpoint = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
model = os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME", "gpt-4o")
delete_resources = os.getenv("DELETE", "true").lower() == "true"

# File to save thread history
THREAD_FILE = "thread_history.json"


def main():
    """Interactive demo with automatic serialization after every message."""
    
    print("\n" + "="*70)
    print("AUTO-SERIALIZATION DEMO: Thread Save/Restore After Every Message")
    print("="*70)
    print("Demo Guide:")
    print("  1. Type a message (e.g. 'I am Alex')")
    print("  2. Agent responds using current conversation context")
    print("  3. State auto-serializes to 'thread_history.json'")
    print("  4. File reloads (deserialization) for next turn")
    print("  5. Type 'quit' to exit the demo")
    print("="*70)
    
    # Initialize project client and OpenAI responses client
    project_client = AIProjectClient(endpoint=endpoint, credential=DefaultAzureCredential())
    openai_client = project_client.get_openai_client()
    
    with project_client:
        # Create agent
        agent = project_client.agents.create_version(
            agent_name="memory-bot",
            definition=PromptAgentDefinition(
                model=model,
                instructions="You are a helpful assistant. Remember everything the user tells you and refer back to it."
            )
        )
        
        print(f"\nAgent created: {agent.name} (version {agent.version})")
        
        # Try to load existing conversation from file, or create new one
        print("Checking for existing thread...")
        conversation_history = []
        message_count = 0
        
        if os.path.exists(THREAD_FILE):
            try:
                print(f"   Found {THREAD_FILE}. Loading previous conversation...")
                with open(THREAD_FILE, 'r', encoding='utf-8') as f:
                    loaded_data = json.load(f)
                
                conversation_history = loaded_data.get('conversation_history', [])
                message_count = loaded_data.get('message_number', 0)
                
                print(f"   Restored previous session with {message_count} messages.")
                print(f"   Continuing from where you left off...\n")
            except Exception as e:
                print(f"   Could not load previous thread: {e}")
                print(f"   Creating new conversation instead...\n")
                conversation_history = []
        else:
            print("   Creating new conversation...")
            print("   New conversation started\n")
        
        print("="*70)
        print("Interactive Chat with Auto-Serialization")
        print("="*70)
        print("After each message:")
        print("   1. Agent responds")
        print("   2. Conversation automatically serializes (saves)")
        print("   3. Conversation automatically deserializes (restores)")
        print("   4. Next message uses restored conversation")
        print("\nType 'quit' to exit")
        print("="*70 + "\n")
        
        while True:
            try:
                user_input = input("You: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nSee you again soon.")
                break
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\nDemo completed.")
                print(f"\nTotal messages: {message_count}")
                print(f"Total serialization cycles: {message_count}")
                break
            
            if not user_input:
                continue
            
            message_count += 1
            print(f"\n[Message #{message_count}]")
            
            # Add user message to conversation
            conversation_history.append({"role": "user", "content": user_input})
            
            # Step 1: Agent responds using current conversation
            print("Agent: ", end="", flush=True)
            response = openai_client.responses.create(
                input=conversation_history,
                extra_body={"agent": {"type": "agent_reference", "name": agent.name, "version": agent.version}}
            )
            
            assistant_text = ""
            if response.status == "completed":
                for item in response.output:
                    if item.type == "message" and item.content and item.content[0].type == "output_text":
                        assistant_text = item.content[0].text
                        print(assistant_text)
            else:
                print(f"Response failed: {response.status}")
            
            # Add assistant response to history
            if assistant_text:
                conversation_history.append({"role": "assistant", "content": assistant_text})
            
            # Step 2: Serialize the conversation (save state)
            print("\n[Auto-Serializing conversation state...]")
            serialized = {
                'timestamp': datetime.now().isoformat(),
                'message_number': message_count,
                'conversation_history': conversation_history
            }
            print(f"   Serialized: {len(str(serialized))} bytes")
            print(f"   Contains: {list(serialized.keys())}")
            
            # Save to JSON file
            print(f"\n[Saving to {THREAD_FILE}...]")
            with open(THREAD_FILE, 'w', encoding='utf-8') as f:
                json.dump(serialized, f, indent=2)
            print(f"   Saved to disk: {THREAD_FILE}")
            
            # Step 3: Load from JSON file and deserialize
            print(f"\n[Loading from {THREAD_FILE}...]")
            with open(THREAD_FILE, 'r', encoding='utf-8') as f:
                loaded_data = json.load(f)
            print(f"   Loaded from disk (message #{loaded_data['message_number']})")
            
            print("\n[Deserializing conversation state...]")
            conversation_history = loaded_data['conversation_history']
            print("   Conversation restored from file")
            print("   Next message will use this restored conversation\n")
            
            print("-" * 70 + "\n")
        
        print("\n" + "="*70)
        print("DEMO COMPLETE")
        print("="*70)
        print("What you saw:")
        print("   • Conversation automatically saved to JSON file after each message")
        print("   • Conversation automatically restored from JSON file")
        print("   • Agent maintained full conversation history")
        print("   • Each cycle proved file persistence works")
        print(f"\nCheck the file: {THREAD_FILE}")
        print("="*70 + "\n")
        
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
