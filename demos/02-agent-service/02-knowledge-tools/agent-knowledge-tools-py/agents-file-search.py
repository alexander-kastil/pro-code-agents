import os
import time
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.agents import AgentsClient
from azure.ai.agents.models import FileSearchToolResource, ToolResources, FileSearchToolDefinition, ListSortOrder

# Demonstrates file search capabilities using Azure AI Agent Service with a vector store.
# The agent searches through uploaded documents to answer questions using the file search tool.
# Requires a pre-configured vector store with documents in Microsoft Foundry.

def main():

    # Clear the console to keep the output focused on the agent interaction
    os.system('cls' if os.name == 'nt' else 'clear')

    # Load environment variables from .env file
    load_dotenv()
    endpoint = os.getenv("PROJECT_ENDPOINT")
    model = os.getenv("MODEL_DEPLOYMENT")
    vector_store_id = os.getenv("VECTOR_STORE_ID")
    delete_resources = os.getenv("DELETE", "true").lower() == "true"

    print(f"Using endpoint: {endpoint}")
    print(f"Using model: {model}")
    print(f"Using vector store: {vector_store_id}")
    print(f"Delete resources: {delete_resources}")

    # Connect to the Azure AI Agent Service in Microsoft Foundry
    agents_client = AgentsClient(
        endpoint=endpoint,
        credential=DefaultAzureCredential()
    )

    with agents_client:
        start = time.time()

        # Create agent with file search tool
        agent = agents_client.create_agent(
            model=model,
            name="file-search-agent",
            instructions="You are a helpful agent that can search through documents to answer questions. Use the file search tool to find relevant information.",
            tools=[FileSearchToolDefinition()],
            tool_resources=ToolResources(
                file_search=FileSearchToolResource(
                    vector_store_ids=[vector_store_id]
                )
            )
        )
        print(f"Created agent: {agent.name}, ID: {agent.id}")

        # Create a thread for the conversation
        thread = agents_client.threads.create()
        print(f"Created thread, thread ID: {thread.id}")

        # Create message in thread
        message = agents_client.messages.create(
            thread_id=thread.id,
            role="user",
            content="Tell me about Equinox Gold"
        )
        print(f"Created message, message ID: {message.id}")

        # Create and poll run
        run = agents_client.runs.create(thread_id=thread.id, agent_id=agent.id)
        print(f"Run started, status: {run.status}")

        # Poll the run until completion
        while run.status in ["queued", "in_progress", "requires_action"]:
            time.sleep(1)
            run = agents_client.runs.get(thread_id=thread.id, run_id=run.id)
            print(f"Run status: {run.status}")

        duration = time.time() - start
        print(f"Run completed (took {duration:.2f}s)")

        if run.status == "failed":
            print(f"Run error: {run.last_error}")

        # Cleanup based on DELETE flag
        if delete_resources:
            agents_client.delete_agent(agent.id)
            print("Deleted agent")
        else:
            print(f"Preserved agent: {agent.id}")

        # List messages in ascending order
        messages = agents_client.messages.list(
            thread_id=thread.id,
            order=ListSortOrder.ASCENDING
        )
        
        print("\n--- Conversation ---")
        for msg in messages:
            if msg.text_messages:
                last_text = msg.text_messages[-1]
                print(f"{msg.role}: {last_text.text.value}\n")


if __name__ == '__main__':
    main()
