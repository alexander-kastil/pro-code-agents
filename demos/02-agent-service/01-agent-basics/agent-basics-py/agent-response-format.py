import os
import io
import sys
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.agents import AgentsClient
from azure.ai.agents.models import ListSortOrder, AgentsResponseFormat, RunStatus

# Configure UTF-8 encoding for Windows console (fixes emoji display issues)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Clear the console to keep the output focused on the agent interaction
os.system('cls' if os.name == 'nt' else 'clear')

# Load environment variables from .env file
load_dotenv()
endpoint = os.getenv("PROJECT_ENDPOINT")
model = os.getenv("MODEL_DEPLOYMENT")

print(f"Using endpoint: {endpoint}")
print(f"Using model: {model}")

# Connect to the Azure AI Foundry project
agents_client = AgentsClient(
    endpoint=endpoint,
    credential=DefaultAzureCredential()
)
with agents_client:

    agent = agents_client.create_agent(
        model=model,
        name="my-agent",
        instructions="You are helpful agent. You will respond with a JSON object.",
        response_format=AgentsResponseFormat(type="json_object"),
    )
    print(f"Created agent, agent ID: {agent.id}")

    thread = agents_client.threads.create()
    print(f"Created thread, thread ID: {thread.id}")

    message = agents_client.messages.create(
        thread_id=thread.id,
        role="user",
        content="Hello, give me a list of planets in our solar system, and their mass in kilograms.",
    )
    print(f"Created message, message ID: {message.id}")

    run = agents_client.runs.create_and_process(thread_id=thread.id, agent_id=agent.id)

    if run.status != RunStatus.COMPLETED:
        print(f"The run did not succeed: {run.status=}.")

    agents_client.delete_agent(agent.id)
    print("Deleted agent")

    messages = agents_client.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)
    for msg in messages:
        if msg.text_messages:
            last_text = msg.text_messages[-1]
            print(f"{msg.role}: {last_text.text.value}")
