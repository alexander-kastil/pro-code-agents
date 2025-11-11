import os
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import ConnectionType
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import AzureAISearchQueryType, AzureAISearchTool, ListSortOrder, MessageRole

def main():
    # Clear the console to keep the output focused on the agent interaction
    os.system('cls' if os.name == 'nt' else 'clear')

    # Load environment variables from .env file
    load_dotenv()
    endpoint = os.getenv("PROJECT_ENDPOINT")
    model = os.getenv("MODEL_DEPLOYMENT")

    print(f"Using endpoint: {endpoint}")
    print(f"Using model: {model}")

    project_client = AIProjectClient(
        endpoint=endpoint,
        credential=DefaultAzureCredential(),
    )

    with project_client:
        agents_client = project_client.agents

        # [START create_agent_with_azure_ai_search_tool]
        conn_id = project_client.connections.get_default(ConnectionType.AZURE_AI_SEARCH).id
        print(conn_id)

        # Initialize agent AI search tool and add the search index connection id
        ai_search = AzureAISearchTool(
            index_connection_id=conn_id,
            index_name="insurance-documents-index",
            query_type=AzureAISearchQueryType.SIMPLE,
            top_k=3,
            filter="",
        )

        agent = agents_client.create_agent(
            model=model,
            name="insurance-rag-agent",
            instructions="You are a helpful agent to knowledgeably answer questions about insurance products using the Azure AI Search tool to retrieve relevant information from the knowledge base.",
            tools=ai_search.definitions,
            tool_resources=ai_search.resources,
        )
        # [END create_agent_with_azure_ai_search_tool]
        print(f"Created agent, agent ID: {agent.id}")

        # Create thread for communication
        thread = agents_client.threads.create()
        print(f"Created thread, thread ID: {thread.id}")

        # Create message to thread
        message = agents_client.messages.create(
            thread_id=thread.id,
            role="user",
            content="Which policies cover a broken car side mirror?",
        )
        print(f"Created message, message ID: {message.id}")

        # Create and process agent run in thread with tools
        run = agents_client.runs.create_and_process(thread_id=thread.id, agent_id=agent.id)
        print(f"Run finished with status: {run.status}")

        if run.status == "failed":
            print(f"Run failed: {run.last_error}")

        # Fetch run steps to get the details of the agent run
        run_steps = agents_client.run_steps.list(thread_id=thread.id, run_id=run.id)
        for step in run_steps:
            print(f"Step {step['id']} status: {step['status']}")
            step_details = step.get("step_details", {})
            tool_calls = step_details.get("tool_calls", [])

            if tool_calls:
                print("  Tool calls:")
                for call in tool_calls:
                    print(f"    Tool Call ID: {call.get('id')}")
                    print(f"    Type: {call.get('type')}")

                    azure_ai_search_details = call.get("azure_ai_search", {})
                    if azure_ai_search_details:
                        print(f"    azure_ai_search input: {azure_ai_search_details.get('input')}")
                        print(f"    azure_ai_search output: {azure_ai_search_details.get('output')}")
            print()  # add an extra newline between steps

        # Delete the agent when done
        agents_client.delete_agent(agent.id)
        print("Deleted agent")

        # [START populate_references_agent_with_azure_ai_search_tool]
        # Fetch and log all messages
        messages = agents_client.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)
        for message in messages:
            if message.role == MessageRole.AGENT and message.url_citation_annotations:
                placeholder_annotations = {
                    annotation.text: f" [see {annotation.url_citation.title}] ({annotation.url_citation.url})"
                    for annotation in message.url_citation_annotations
                }
                for message_text in message.text_messages:
                    message_str = message_text.text.value
                    for k, v in placeholder_annotations.items():
                        message_str = message_str.replace(k, v)
                    print(f"{message.role}: {message_str}")
            else:
                for message_text in message.text_messages:
                    print(f"{message.role}: {message_text.text.value}")
        # [END populate_references_agent_with_azure_ai_search_tool]


if __name__ == '__main__':
    main()
