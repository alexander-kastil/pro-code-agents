import os
import io
import sys
import time
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.agents import AgentsClient
from azure.ai.agents.models import ListSortOrder

# Configure UTF-8 encoding for Windows console (fixes emoji display issues)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def main():

    # Clear the console to keep the output focused on the agent interaction
    os.system('cls' if os.name == 'nt' else 'clear')

    # Load environment variables from .env file
    load_dotenv()
    endpoint = os.getenv("PROJECT_ENDPOINT")
    model = os.getenv("MODEL_DEPLOYMENT")

    print(f"Using endpoint: {endpoint}")
    print(f"Using model: {model}")

    # Create separate AgentsClient for agent operations
    agents_client = AgentsClient(
        endpoint=endpoint,
        credential=DefaultAzureCredential()
    )
    
    with agents_client:

        agent = agents_client.create_agent(
            model=model,
            name="basic-agent",
            instructions="You are helpful agent"
        )

        print(f"Created agent: {agent.name}, ID: {agent.id}")

        # Create a thread for the conversation
        thread = agents_client.threads.create()
        print(f"Created thread, thread ID: {thread.id}")

        # [START create_message]
        message = agents_client.messages.create(
            thread_id=thread.id,
            role="user",
            content="Hello, tell me a joke"
        )
        # [END create_message]
        print(f"Created message, message ID: {message.id}")

        # [START create_run]
        run = agents_client.runs.create(thread_id=thread.id, agent_id=agent.id)

        # Poll the run as long as run status is queued or in progress
        while run.status in ["queued", "in_progress", "requires_action"]:
            # Wait for a second between status checks
            time.sleep(1)
            run = agents_client.runs.get(thread_id=thread.id, run_id=run.id)
            # [END create_run]
            print(f"Run status: {run.status}")

        if run.status == "failed":
            print(f"Run error: {run.last_error}")

        agents_client.delete_agent(agent.id)
        print("Deleted agent")

        # [START list_messages]
        messages = agents_client.messages.list(
            thread_id=thread.id,
            order=ListSortOrder.ASCENDING
        )
        for msg in messages:
            if msg.text_messages:
                last_text = msg.text_messages[-1]
                print(f"{msg.role}: {last_text.text.value}")
        # [END list_messages]


if __name__ == '__main__':
    main()
