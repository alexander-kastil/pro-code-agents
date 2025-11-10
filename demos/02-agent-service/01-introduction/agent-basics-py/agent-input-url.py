import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.agents.models import (
    ListSortOrder,
    MessageTextContent,
    MessageInputContentBlock,
    MessageImageUrlParam,
    MessageInputTextBlock,
    MessageInputImageUrlBlock,
    RunStatus,
)
from typing import List

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
        instructions="You are helpful agent",
    )
    print(f"Created agent, agent ID: {agent.id}")

    thread = agents_client.agents.threads.create()
    print(f"Created thread, thread ID: {thread.id}")

    image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg"
    input_message = "Hello, what is in the image ?"
    url_param = MessageImageUrlParam(url=image_url, detail="high")
    content_blocks: List[MessageInputContentBlock] = [
        MessageInputTextBlock(text=input_message),
        MessageInputImageUrlBlock(image_url=url_param),
    ]
    message = agents_client.agents.messages.create(thread_id=thread.id, role="user", content=content_blocks)
    print(f"Created message, message ID: {message.id}")

    run = agents_client.agents.runs.create_and_process(thread_id=thread.id, agent_id=agent.id)

    if run.status != RunStatus.COMPLETED:
        print(f"The run did not succeed: {run.status=}.")

    agents_client.agents.delete_agent(agent.id)
    print("Deleted agent")

    messages = agents_client.agents.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)
    for msg in messages:
        last_part = msg.content[-1]
        if isinstance(last_part, MessageTextContent):
            print(f"{msg.role}: {last_part.text.value}")
