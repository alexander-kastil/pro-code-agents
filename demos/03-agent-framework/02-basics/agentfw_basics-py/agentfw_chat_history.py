"""
Chat history demo: demonstrates chat history management using reducers.

This file shows two reducers:
 - MessageCountingChatReducer: keeps only the last N messages
 - SummarizingChatReducer: when message count passes a threshold, summarizes
   older messages into a single summary message using the LLM and replaces them
   with the summary (reduces storage size while preserving context).

The demo runs an interactive loop: it accepts user input, runs the agent, 
stores the exchange to an in-memory store, and prints the stored messages 
count and contents.

Features:
 - Serialization: automatically saves chat history to JSON after each update
 - Deserialization: on startup, prompts to load previous conversation history
 - Reusable utilities: all chat history classes are in utils/chat_history.py
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition

from utils.chat_history import (
    SimpleMessage,
    MessageCountingChatReducer,
    SummarizingChatReducerFoundry,
    InMemoryChatMessageStore
)

# Load environment variables
load_dotenv()

endpoint = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
model = os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME", "gpt-4o")
delete_resources = os.getenv("DELETE", "true").lower() == "true"

# Chat history file path
HISTORY_FILE = os.path.join("output", "chat_history.json")


def main():
    print("\n" + "=" * 70)
    print("DEMO: Chat History Management with Reducers")
    print("=" * 70)

    if not endpoint:
        print("\nMissing Azure AI configuration. Please set AZURE_AI_PROJECT_ENDPOINT in your environment or .env file.")
        return

    # Initialize project client and OpenAI responses client
    project_client = AIProjectClient(endpoint=endpoint, credential=DefaultAzureCredential())
    openai_client = project_client.get_openai_client()

    with project_client:
        # Create primary chat agent
        chat_agent = project_client.agents.create_version(
            agent_name="chat-history-agent",
            definition=PromptAgentDefinition(
                model=model,
                instructions="You are a friendly assistant. Answer clearly and concisely."
            )
        )

        # Create a lightweight summarizer agent (same endpoint but different instructions)
        summarizer_agent = project_client.agents.create_version(
            agent_name="summarizer-agent",
            definition=PromptAgentDefinition(
                model=model,
                instructions=(
                    "You are a concise summarizer. Produce a short summary of a conversation. "
                    "Return only plain text, no JSON or extra commentary."
                )
            )
        )

        print(f"\nChat agent created: {chat_agent.name} (version {chat_agent.version})")
        print(f"Summarizer agent created: {summarizer_agent.name} (version {summarizer_agent.version})")

        # Create reducers and message store
        msg_count_reducer = MessageCountingChatReducer(target_count=12)
        summarizing_reducer = SummarizingChatReducerFoundry(
            openai_client=openai_client,
            agent_name=summarizer_agent.name,
            agent_version=summarizer_agent.version,
            threshold=10,
            retain_last=4
        )

        # Chain reducers: summarizing first (reduce old messages), then counting as safeguard
        store = InMemoryChatMessageStore(
            reducers=[summarizing_reducer, msg_count_reducer],
            auto_save_path=HISTORY_FILE
        )

        print("\nAgents created and in-memory message store initialized.")
        
        # Prompt user to load previous conversation history
        if Path(HISTORY_FILE).exists():
            print(f"\nFound existing conversation history: {HISTORY_FILE}")
            try:
                load_choice = input("Do you want to load the conversation history? (y/n): ").strip().lower()
                if load_choice in ['y', 'yes']:
                    store.load_from_file(HISTORY_FILE)
                    messages_loaded = store.get_messages_sync()
                    print(f"Loaded {len(messages_loaded)} message(s) from history.")
                else:
                    print("Starting with empty history.")
            except (EOFError, KeyboardInterrupt):
                print("\nStarting with empty history.")
        else:
            print("\nNo previous history found. Starting fresh.")
        
        print("\nType 'quit' to exit.\n")

        # Interactive loop
        while True:
            try:
                user_input = input("You: ")
            except (EOFError, KeyboardInterrupt):
                print("\nExiting chat demo.")
                break

            if not user_input or user_input.strip().lower() in {"quit", "exit", "q"}:
                print("\nGoodbye!")
                break

            # Add user message to the store
            store.add_message_sync(SimpleMessage(role="user", text=user_input))

            # Prepare messages to send to the agent
            history = store.get_messages_sync()
            
            # Build conversation history for Foundry API
            conversation_messages = []
            for m in history:
                conversation_messages.append({"role": m.role, "content": m.text})

            # Run agent using Foundry Responses API
            try:
                response = openai_client.responses.create(
                    input=conversation_messages,
                    extra_body={"agent": {"type": "agent_reference", "name": chat_agent.name, "version": chat_agent.version}}
                )

                assistant_text = ""
                if response.status == "completed":
                    for item in response.output:
                        if item.type == "message" and item.content and item.content[0].type == "output_text":
                            assistant_text = item.content[0].text.strip()

                # Print assistant reply
                print(f"Assistant: {assistant_text}\n")

                # Add assistant message to the store
                if assistant_text:
                    store.add_message_sync(SimpleMessage(role="assistant", text=assistant_text))

            except Exception as e:
                print(f"\nError calling agent: {e}")

            # Show current stored messages
            messages_in_store = store.get_messages_sync()
            print(f"- Number of messages in store: {len(messages_in_store)}")
            for idx, m in enumerate(messages_in_store, start=1):
                # Truncate long messages for display
                text_preview = (m.text[:200] + "...") if len(m.text) > 200 else m.text
                print(f"  {idx}. {m.role}: {text_preview}")

            print("\n" + "-" * 60 + "\n")

        # Cleanup based on DELETE flag
        if delete_resources:
            project_client.agents.delete_version(agent_name=chat_agent.name, agent_version=chat_agent.version)
            project_client.agents.delete_version(agent_name=summarizer_agent.name, agent_version=summarizer_agent.version)
            print("Deleted agent versions")
        else:
            print(f"Agents preserved: {chat_agent.name}:{chat_agent.version}, {summarizer_agent.name}:{summarizer_agent.version}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nDemo interrupted.")
    except Exception as e:
        print(f"\nError: {e}")
