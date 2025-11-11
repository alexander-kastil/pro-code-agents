import os
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import ListSortOrder, MessageRole, SharepointTool

def main():
    # Clear the console to keep the output focused on the agent interaction
    os.system('cls' if os.name == 'nt' else 'clear')

    # Load environment variables from .env file
    load_dotenv()
    endpoint = os.getenv("PROJECT_ENDPOINT")
    model = os.getenv("MODEL_DEPLOYMENT")
    sharepoint_connection_name = os.getenv("SHAREPOINT_CONNECTION")

    print(f"Using endpoint: {endpoint}")
    print(f"Using model: {model}")
    print(f"SharePoint connection: {sharepoint_connection_name}")

    project_client = AIProjectClient(
        endpoint=endpoint,
        credential=DefaultAzureCredential(),
    )

    conn_id = project_client.connections.get(sharepoint_connection_name).id
    print(f"Connection ID: {conn_id}")

    conn_id = project_client.connections.get(sharepoint_connection_name).id
    print(f"Connection ID: {conn_id}")

    # Initialize Sharepoint tool with connection id
    sharepoint = SharepointTool(connection_id=conn_id)

    # Create agent with Sharepoint tool and process agent run
    with project_client:
        agents_client = project_client.agents

        agent = agents_client.create_agent(
            model=model,
            name="my-agent",
            instructions="You are a helpful agent",
            tools=sharepoint.definitions,
        )
        print(f"Created agent, agent ID: {agent.id}")

        # Create thread for communication
        thread = agents_client.threads.create()
        print(f"Created thread, thread ID: {thread.id}")

        # Create message to thread
        message = agents_client.messages.create(
            thread_id=thread.id,
            role="user",
            content="Hello, summarize the key points of the <sharepoint_resource_document>",
        )
        print(f"Created message, message ID: {message.id}")

        # Create and process agent run in thread with tools
        run = agents_client.runs.create_and_process(thread_id=thread.id, agent_id=agent.id)
        print(f"Run finished with status: {run.status}")

        if run.status == "failed":
            # Check if you got "Rate limit is exceeded.", then you want to get more quota
            print(f"Run failed: {run.last_error}")

        # Delete the agent when done
        agents_client.delete_agent(agent.id)
        print("Deleted agent")

        # Fetch and log all messages
        messages = agents_client.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)
        print("\nConversation:")
        print("-" * 50)
        for msg in messages:
            if msg.text_messages:
                responses = []
                for text_message in msg.text_messages:
                    responses.append(text_message.text.value)
                message_text = " ".join(responses)
                for annotation in msg.url_citation_annotations:
                    message_text = message_text.replace(
                        annotation.text, f" [{annotation.url_citation.title}]({annotation.url_citation.url})"
                    )
                print(f"{msg.role}: {message_text}")
                print("-" * 50)


if __name__ == '__main__':
    main()
