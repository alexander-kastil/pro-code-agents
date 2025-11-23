import os
import io
import sys
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.agents import AgentsClient
from azure.ai.agents.models import (
    ListSortOrder,
    MessageTextContent,
    MessageInputContentBlock,
    MessageImageFileParam,
    MessageInputTextBlock,
    MessageInputImageFileBlock,
    FilePurpose,
    RunStatus,
)
from typing import List

# Configure UTF-8 encoding for Windows console (fixes emoji display issues)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

asset_file_path = os.path.join(os.path.dirname(__file__), "assets/soi.jpg")

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
        instructions="You are helpful agent",
    )
    print(f"Created agent, agent ID: {agent.id}")

    thread = agents_client.threads.create()
    print(f"Created thread, thread ID: {thread.id}")

    image_file = agents_client.files.upload_and_poll(file_path=asset_file_path, purpose=FilePurpose.AGENTS)
    print(f"Uploaded file, file ID: {image_file.id}")

    input_message = "Hello, what is in the image ?"
    file_param = MessageImageFileParam(file_id=image_file.id, detail="high")
    content_blocks: List[MessageInputContentBlock] = [
        MessageInputTextBlock(text=input_message),
        MessageInputImageFileBlock(image_file=file_param),
    ]
    message = agents_client.messages.create(thread_id=thread.id, role="user", content=content_blocks)
    print(f"Created message, message ID: {message.id}")

    run = agents_client.runs.create_and_process(thread_id=thread.id, agent_id=agent.id)

    if run.status != RunStatus.COMPLETED:
        print(f"The run did not succeed: {run.status=}.")

    agents_client.delete_agent(agent.id)
    print("Deleted agent")

    messages = agents_client.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)
    for msg in messages:
        last_part = msg.content[-1]
        if isinstance(last_part, MessageTextContent):
            print(f"{msg.role}: {last_part.text.value}")
