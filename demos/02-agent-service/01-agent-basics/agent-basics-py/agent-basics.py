import os
import io
import sys
import time
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition
from openai import OpenAI  # type: ignore

# Configure UTF-8 encoding for Windows console (fixes emoji display issues)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def main():
    # Clear console
    os.system('cls' if os.name == 'nt' else 'clear')

    load_dotenv()
    endpoint = os.getenv("PROJECT_ENDPOINT")
    model = os.getenv("MODEL_DEPLOYMENT")
    delete_resources = os.getenv("DELETE", "true").lower() == "true"

    print(f"Using endpoint: {endpoint}")
    print(f"Using model: {model}")
    print(f"Delete resources: {delete_resources}")

    # Initialize project client and OpenAI responses client
    project_client = AIProjectClient(endpoint=endpoint, credential=DefaultAzureCredential())
    openai_client = project_client.get_openai_client()

    with project_client:
        start = time.time()
        # Create versioned agent (prompt kind)
        agent = project_client.agents.create_version(
            agent_name="basic-agent",
            definition=PromptAgentDefinition(
                model=model,
                instructions="You are helpful agent"
            )
        )
        print(f"Created agent: {agent.name} (version {agent.version})")

        # Create response with user input (no separate thread/run needed now)
        user_input = "Hello, tell me a joke"
        response = openai_client.responses.create(
            input=user_input,
            extra_body={"agent": {"type": "agent_reference", "name": agent.name, "version": agent.version}}
        )

        # Status / timing
        duration = time.time() - start
        print(f"Response status: {response.status} (took {duration:.2f}s)")
        if response.error:
            print(f"Response error: {response.error}")

        # Output items
        for item in response.output:
            if item.type == "message" and item.content and item.content[0].type == "output_text":
                print(f"assistant: {item.content[0].text}")

        # Cleanup based on DELETE flag
        if delete_resources:
            project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
            print("Deleted agent version")
        else:
            print(f"Preserved agent: {agent.name}:{agent.version}")


if __name__ == '__main__':
    main()
