import os
import json
from datetime import datetime
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition

# Load environment
load_dotenv('.env')

endpoint = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
model = os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME", "gpt-4o")
delete_resources = os.getenv("DELETE", "true").lower() == "true"

# File for persisting memory profile only
OUTPUT_PATH = os.getenv("OUTPUT_PATH", "./output")
MEMORY_FILE = os.path.join(OUTPUT_PATH, "ai_memory_profile.json")


class AIMemoryExtractor:
    """
    AI-powered memory: Let the AI decide what's important to remember!
    No hardcoded patterns - the AI analyzes conversations intelligently.
    With persistent file storage!
    """
    
    def __init__(self, openai_client, agent_name, agent_version, memory_file=MEMORY_FILE):
        self.user_profile = {}  # Long-term memory storage
        self.openai_client = openai_client
        self.agent_name = agent_name
        self.agent_version = agent_version
        self.memory_file = memory_file
        
        # Load existing profile from file
        self._load_profile()
    
    def _load_profile(self):
        """Load user profile from JSON file."""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.user_profile = data.get('profile', {})
                print(f"\n📂 [LOADED MEMORY] from {self.memory_file}")
                if self.user_profile:
                    print(f"   🧠 Restored profile: {', '.join([f'{k}={v}' for k, v in self.user_profile.items()])}")
                else:
                    print(f"   File exists but profile is empty")
            except Exception as e:
                print(f"\n⚠️  [LOAD ERROR] Could not load {self.memory_file}: {e}")
                self.user_profile = {}
        else:
            print(f"\n[NEW MEMORY] No existing memory file found")
    
    def _save_profile(self):
        """Save user profile to JSON file."""
        try:
            # Ensure output directory exists
            os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
            
            data = {
                'timestamp': datetime.now().isoformat(),
                'profile': self.user_profile
            }
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"   💾 [SAVED TO FILE] {self.memory_file}")
        except Exception as e:
            print(f"   ⚠️  [SAVE ERROR] Could not save to {self.memory_file}: {e}")
    
    def get_profile_context(self) -> str:
        """Get profile context to inject before agent processes request."""
        
        # If we have profile data, create context
        if self.user_profile:
            profile_text = "\n".join([f"- {k}: {v}" for k, v in self.user_profile.items()])
            
            print(f"\n   💭 [INJECTING LONG-TERM MEMORY]")
            print(f"   Profile: {', '.join([f'{k}={v}' for k, v in self.user_profile.items()])}\n")
            
            instructions = f"""[USER PROFILE - LONG-TERM MEMORY]:
{profile_text}

IMPORTANT: This is information about the user that persists across all conversations.
Reference this naturally when relevant, and be enthusiastic when recognizing the user!"""
            
            return instructions
        
        return ""
    
    def extract_and_learn(self, user_message: str):
        """Let AI extract important information AFTER conversation."""
        
        if not user_message or len(user_message) < 3:
            return
        
        print(f"   [AI ANALYZING]: '{user_message}'")
        
        # Ask AI to extract important information
        analysis_prompt = f"""Analyze this user message and extract any personal information worth remembering for future conversations.

User message: "{user_message}"

Current profile: {self.user_profile if self.user_profile else "Empty"}

Extract ONLY factual information about the user (name, age, profession, preferences, hobbies, etc.).
Return as JSON format: {{"key": "value", "key2": "value2"}}
If nothing important, return empty: {{}}

Examples:
- "My name is Alice" → {{"name": "Alice"}}
- "I'm a teacher" → {{"profession": "teacher"}}
- "I love pizza and my favorite color is blue" → {{"favorite_food": "pizza", "favorite_color": "blue"}}
- "How are you?" → {{}}

Extract only NEW or UPDATED information. Be concise with values.
JSON only, no explanation:"""

        try:
            # Use AI to analyze the message
            response = self.openai_client.responses.create(
                input=[{"role": "user", "content": analysis_prompt}],
                extra_body={"agent": {"type": "agent_reference", "name": self.agent_name, "version": self.agent_version}}
            )
            
            # Parse AI response
            ai_response = ""
            if response.status == "completed":
                for item in response.output:
                    if item.type == "message" and item.content and item.content[0].type == "output_text":
                        ai_response = item.content[0].text.strip()
                        break
            
            # Try to extract JSON
            if "{" in ai_response and "}" in ai_response:
                start = ai_response.index("{")
                end = ai_response.rindex("}") + 1
                json_str = ai_response[start:end]
                
                extracted = json.loads(json_str)
                
                # Update profile with extracted information
                if extracted:
                    for key, value in extracted.items():
                        self.user_profile[key] = value
                        print(f"   💾 [AI LEARNED] {key} = {value}")
                    
                    # Save to file immediately after learning
                    self._save_profile()
        
        except Exception as e:
            print(f"   ⚠️  [AI EXTRACTION ERROR]: {e}")


def main():
    print("\n" + "="*70)
    print("AI-POWERED LONG-TERM MEMORY with FILE PERSISTENCE")
    print("="*70)
    print("\nConcept: AI intelligently extracts & saves important information!")
    print(f"Memory File: {MEMORY_FILE}")
    print("="*70)
    
    # Initialize project client and OpenAI responses client
    project_client = AIProjectClient(endpoint=endpoint, credential=DefaultAzureCredential())
    openai_client = project_client.get_openai_client()
    
    with project_client:
        print("\n🔧 Creating agent with AI-powered memory...")
        
        # Create main chat agent
        chat_agent = project_client.agents.create_version(
            agent_name="memory-chat-agent",
            definition=PromptAgentDefinition(
                model=model,
                instructions="""You are a helpful, friendly assistant with long-term memory.

When you recognize information about the user from their profile:
- Reference it naturally in conversation
- Be enthusiastic when you recognize them
- Provide personalized responses based on what you know

Be conversational and warm!"""
            )
        )
        
        # Create memory extractor agent (lightweight)
        memory_agent = project_client.agents.create_version(
            agent_name="memory-extractor-agent",
            definition=PromptAgentDefinition(
                model=model,
                instructions="You are an information extractor. Extract factual information about users."
            )
        )
        
        print(f"   Chat agent created: {chat_agent.name} (version {chat_agent.version})")
        print(f"   Memory agent created: {memory_agent.name} (version {memory_agent.version})")
        
        # Create AI-powered memory provider
        ai_memory = AIMemoryExtractor(openai_client, memory_agent.name, memory_agent.version)
        print("   AI memory analyzer initialized\n")
        
        print("="*70)
        print("COMMANDS:")
        print("="*70)
        print("  • Chat naturally - AI extracts & saves info to file")
        print("  • 'new' - Start new conversation (test cross-conversation memory)")
        print("  • 'profile' - Show what AI learned about you")
        print("  • 'quit' - Exit")
        print("="*70)
        
        # Start conversation loop
        conversation_num = 0
        conversation_history = []
        
        try:
            while True:
                # Create new conversation if needed
                if not conversation_history:
                    conversation_num += 1
                    conversation_history = []
                    print(f"\n🆕 CONVERSATION #{conversation_num} started\n")
                
                # Get user input
                try:
                    user_input = input("You: ").strip()
                except (EOFError, KeyboardInterrupt):
                    print("\nSee you again soon.")
                    break
                
                if not user_input:
                    continue
                
                # Handle commands
                if user_input.lower() == 'quit':
                    print("\nDemo ended!")
                    if ai_memory.user_profile:
                        print("\n📊 Final AI-Learned Profile:")
                        for key, value in ai_memory.user_profile.items():
                            print(f"   • {key}: {value}")
                    else:
                        print("   (No profile data learned)")
                    break
                
                if user_input.lower() == 'new':
                    conversation_history = []  # Will create new conversation on next iteration
                    continue
                
                if user_input.lower() == 'profile':
                    print("\nAI-LEARNED PROFILE:")
                    if ai_memory.user_profile:
                        for key, value in ai_memory.user_profile.items():
                            print(f"   • {key}: {value}")
                    else:
                        print("   (AI hasn't learned anything about you yet)")
                    print()
                    continue
                
                # Get profile context to inject
                profile_context = ai_memory.get_profile_context()
                
                # Add user message to history
                conversation_history.append({"role": "user", "content": user_input})
                
                # Build messages with profile context if available
                messages_to_send = []
                if profile_context:
                    messages_to_send.append({"role": "system", "content": profile_context})
                messages_to_send.extend(conversation_history)
                
                # Send message to agent
                print(f"Agent (Conversation #{conversation_num}): ", end="", flush=True)
                response = openai_client.responses.create(
                    input=messages_to_send,
                    extra_body={"agent": {"type": "agent_reference", "name": chat_agent.name, "version": chat_agent.version}}
                )
                
                assistant_text = ""
                if response.status == "completed":
                    for item in response.output:
                        if item.type == "message" and item.content and item.content[0].type == "output_text":
                            assistant_text = item.content[0].text
                            print(assistant_text)
                
                # Add assistant response to history
                if assistant_text:
                    conversation_history.append({"role": "assistant", "content": assistant_text})
                
                print()
                
                # Extract and learn from user message (AI memory automatically learns)
                ai_memory.extract_and_learn(user_input)
                print()
        
        finally:
            # Cleanup
            print("\nCleaning up...")
            if delete_resources:
                project_client.agents.delete_version(agent_name=chat_agent.name, agent_version=chat_agent.version)
                project_client.agents.delete_version(agent_name=memory_agent.name, agent_version=memory_agent.version)
                print("Deleted agent versions")
            else:
                print(f"Agents preserved: {chat_agent.name}:{chat_agent.version}, {memory_agent.name}:{memory_agent.version}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nSee you again soon.")
