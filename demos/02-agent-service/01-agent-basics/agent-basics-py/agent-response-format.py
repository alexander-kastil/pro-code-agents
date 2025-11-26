import os
import io
import sys
import time
import json
from openai import AuthenticationError  # type: ignore
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition
from openai import OpenAI  # type: ignore

# Configure UTF-8 encoding for Windows console (fixes emoji display issues)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def main():
    # Clear console for focused output
    os.system('cls' if os.name == 'nt' else 'clear')

    load_dotenv()
    endpoint = os.getenv("PROJECT_ENDPOINT")
    model = os.getenv("MODEL_DEPLOYMENT")
    delete_resources = os.getenv("DELETE", "true").lower() == "true"

    print(f"Using endpoint: {endpoint}")
    print(f"Using model: {model}")
    print(f"Delete resources: {delete_resources}")

    # Initialize project + responses client
    project_client = AIProjectClient(endpoint=endpoint, credential=DefaultAzureCredential())
    openai_client: OpenAI = project_client.get_openai_client()

    with project_client:
        start = time.time()
        # Create a versioned prompt agent. We no longer specify response_format here; it's set per response.
        agent = project_client.agents.create_version(
            agent_name="json-format-agent",
            definition=PromptAgentDefinition(
                model=model,
                instructions="You are a helpful agent. Always respond with ONLY a valid JSON object, no extra commentary."
            )
        )
        print(f"Created agent: {agent.name} (version {agent.version})")

        user_input = "List the planets in our solar system with their approximate mass in kilograms. Use keys: name, mass_kg."  # simplified prompt

        # Request a JSON object response using the Responses API
        try:
            response = openai_client.responses.create(
                input=user_input,
                extra_body={"agent": {"type": "agent_reference", "name": agent.name, "version": agent.version}}
            )
        except AuthenticationError as auth_err:
            print(f"Authentication failed: {auth_err}")
            if delete_resources:
                project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
                print("Deleted agent version after auth failure")
            return

        duration = time.time() - start
        print(f"Response status: {response.status} (took {duration:.2f}s)")
        if response.error:
            print(f"Response error: {response.error}")

        raw_json_text = None
        for item in response.output:
            if item.type == "message":
                for content_block in item.content:
                    if content_block.type == "output_text":
                        raw_json_text = content_block.text
                        break
            if raw_json_text:
                break

        if raw_json_text is None:
            print("No JSON text found in response output.")
        else:
            print("Raw JSON text:")
            print(raw_json_text)
            # Attempt to parse
            try:
                parsed = json.loads(raw_json_text)
                print("Parsed JSON object:")
                print(json.dumps(parsed, indent=2))
            except json.JSONDecodeError as e:
                print(f"Failed to parse JSON: {e}")

        if delete_resources:
            project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
            print("Deleted agent version")
        else:
            print(f"Preserved agent: {agent.name}:{agent.version}")

if __name__ == "__main__":
    main()
