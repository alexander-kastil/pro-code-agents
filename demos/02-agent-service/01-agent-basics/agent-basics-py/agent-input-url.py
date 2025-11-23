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
    MessageImageUrlParam,
    MessageInputTextBlock,
    MessageInputImageUrlBlock,
    RunStatus,
)
from typing import List

# Configure UTF-8 encoding for Windows console (fixes emoji display issues)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Clear the console to keep the output focused on the agent interaction
os.system('cls' if os.name == 'nt' else 'clear')

# Load environment variables from .env file
load_dotenv()
endpoint = os.getenv("PROJECT_ENDPOINT")
model = os.getenv("IMG_MODEL_DEPLOYMENT")

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

    # Try a simpler, more reliable image URL
    image_url = "https://raw.githubusercontent.com/Azure-Samples/cognitive-services-sample-data-files/master/ComputerVision/Images/landmark.jpg"
    input_message = "Hello, what is in the image ?"
    url_param = MessageImageUrlParam(url=image_url, detail="high")
    content_blocks: List[MessageInputContentBlock] = [
        MessageInputTextBlock(text=input_message),
        MessageInputImageUrlBlock(image_url=url_param),
    ]
    message = agents_client.messages.create(thread_id=thread.id, role="user", content=content_blocks)
    print(f"Created message, message ID: {message.id}")

    run = agents_client.runs.create_and_process(thread_id=thread.id, agent_id=agent.id)

    if run.status != RunStatus.COMPLETED:
        print(f"The run did not succeed: {run.status=}.")
        if run.last_error:
            print(f"Error details: {run.last_error}")

    agents_client.delete_agent(agent.id)
    print("Deleted agent")

    messages = agents_client.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)
    for msg in messages:
        last_part = msg.content[-1]
        if isinstance(last_part, MessageTextContent):
            print(f"{msg.role}: {last_part.text.value}")
