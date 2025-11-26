import os
import io
import sys
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition
from azure.identity import DefaultAzureCredential
from typing import Any, Optional

# Configure UTF-8 encoding for Windows console (fixes emoji display issues)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Clear the console to keep the output focused on the agent interaction
os.system('cls' if os.name == 'nt' else 'clear')

# Load environment variables from .env file
load_dotenv()
endpoint = os.getenv("PROJECT_ENDPOINT")
model = os.getenv("MODEL_DEPLOYMENT")
delete_enabled = os.getenv("DELETE", "false").lower() == "true"

project_client = AIProjectClient(
    endpoint=endpoint,
    credential=DefaultAzureCredential(),
)

with project_client:
    try:
        # Get the OpenAI client for conversations and responses
        openai_client = project_client.get_openai_client()

        # Create an agent
        agent = project_client.agents.create_version(
            agent_name="event-handler-agent",
            definition=PromptAgentDefinition(
                model=model,
                instructions="You are a helpful agent",
            )
        )
        print(f"Created agent: {agent.name}, Version: {agent.version}")

        # Create a streaming response
        print("\n[START create_stream]")
        response = openai_client.responses.create(
            input=[
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": "Hello, tell me a joke"}
                    ]
                }
            ],
            extra_body={
                "agent": {
                    "type": "agent_reference",
                    "name": agent.name,
                    "version": agent.version
                }
            }
        )

        # Process the response
        print(f"Response status: {response.status}")
        if response.status == "completed":
            for output_item in response.output:
                if output_item.type == "message":
                    print(f"{output_item.role}: {output_item.content[0].text}")
        else:
            print(f"Response failed with status: {response.status}")

        print("[END create_stream]\n")

        # Cleanup
        if delete_enabled:
            project_client.agents.delete_version(
                agent_name=agent.name,
                agent_version=agent.version
            )
            print("Deleted agent")
        else:
            print(f"Skipping cleanup (DELETE={delete_enabled}). Agent {agent.name} version {agent.version} still exists.")
    except Exception as e:
        print(f"Error occurred: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
