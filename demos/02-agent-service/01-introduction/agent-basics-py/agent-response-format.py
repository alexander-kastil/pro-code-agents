import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.agents.models import ListSortOrder, AgentsResponseFormat, RunStatus

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
        name="my-agent",
        instructions="You are helpful agent. You will respond with a JSON object.",
        response_format=AgentsResponseFormat(type="json_object"),
    )
    print(f"Created agent, agent ID: {agent.id}")

    thread = agents_client.agents.threads.create()
    print(f"Created thread, thread ID: {thread.id}")

    message = agents_client.agents.messages.create(
        thread_id=thread.id,
        role="user",
        content="Hello, give me a list of planets in our solar system, and their mass in kilograms.",
    )
    print(f"Created message, message ID: {message.id}")

    run = agents_client.agents.runs.create_and_process(thread_id=thread.id, agent_id=agent.id)

    if run.status != RunStatus.COMPLETED:
        print(f"The run did not succeed: {run.status=}.")

    agents_client.agents.delete_agent(agent.id)
    print("Deleted agent")

    messages = agents_client.agents.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)
    for msg in messages:
        if msg.text_messages:
            last_text = msg.text_messages[-1]
            print(f"{msg.role}: {last_text.text.value}")
