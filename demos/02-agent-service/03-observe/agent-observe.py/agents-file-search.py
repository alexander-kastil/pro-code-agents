import os
import time
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.agents.models import ListSortOrder

def main():

    # Clear the console to keep the output focused on the agent interaction
    os.system('cls' if os.name == 'nt' else 'clear')

    # Load environment variables from .env file
    load_dotenv()
    endpoint = os.getenv("PROJECT_ENDPOINT")
    model = os.getenv("MODEL_DEPLOYMENT")

    print(f"Using endpoint: {endpoint}")
    print(f"Using model: {model}")

    # Connect to the Azure AI Foundry project
    agents_client = AIProjectClient(
        endpoint=endpoint,
        credential=DefaultAzureCredential()
    )
    with agents_client:

        agent = agents_client.agents.create_agent(
            model=model,
            name="basic-agent",
            instructions="You are helpful agent",
            description="Demonstrates basic agent setup and message interaction without specialized tools - a simple conversational agent."
        )

        print(f"Created agent: {agent.name}, ID: {agent.id}")

        # Create a thread for the conversation
        thread = agents_client.agents.threads.create()
        print(f"Created thread, thread ID: {thread.id}")

        # [START create_message]
        message = agents_client.agents.messages.create(
            thread_id=thread.id,
            role="user",
            content="Hello, tell me a joke"
        )
        # [END create_message]
        print(f"Created message, message ID: {message.id}")

        # [START create_run]
        run = agents_client.agents.runs.create(thread_id=thread.id, agent_id=agent.id)

        # Poll the run as long as run status is queued or in progress
        while run.status in ["queued", "in_progress", "requires_action"]:
            # Wait for a second between status checks
            time.sleep(1)
            run = agents_client.agents.runs.get(thread_id=thread.id, run_id=run.id)
            # [END create_run]
            print(f"Run status: {run.status}")

        if run.status == "failed":
            print(f"Run error: {run.last_error}")

        delete_on_exit = os.getenv("DELETE_AGENT_ON_EXIT", "true").lower() == "true"
        if delete_on_exit:
            agents_client.agents.delete_agent(agent.id)
            print("Deleted agent")
        else:
            print(f"Agent {agent.id} preserved for examination in Azure AI Foundry")

        # [START list_messages]
        messages = agents_client.agents.messages.list(
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
