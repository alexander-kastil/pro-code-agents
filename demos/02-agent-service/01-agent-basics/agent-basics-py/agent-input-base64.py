import os, base64
import io
import sys
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition

# Configure UTF-8 encoding for Windows console (fixes emoji display issues)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

asset_file_path = os.path.join(os.path.dirname(__file__), "assets/soi.jpg")

def image_to_base64(image_path: str) -> str:
    """
    Convert an image file to a Base64-encoded string.

    :param image_path: The path to the image file (e.g. 'image_file.png')
    :return: A Base64-encoded string representing the image.
    :raises FileNotFoundError: If the provided file path does not exist.
    :raises OSError: If there's an error reading the file.
    """
    if not os.path.isfile(image_path):
        raise FileNotFoundError(f"File not found at: {image_path}")

    try:
        with open(image_path, "rb") as image_file:
            file_data = image_file.read()
        return base64.b64encode(file_data).decode("utf-8")
    except Exception as exc:
        raise OSError(f"Error reading file '{image_path}'") from exc


# Clear the console to keep the output focused on the agent interaction
os.system('cls' if os.name == 'nt' else 'clear')

load_dotenv()
endpoint = os.getenv("PROJECT_ENDPOINT")
model = os.getenv("MODEL_DEPLOYMENT")
delete_resources = os.getenv("DELETE", "true").lower() == "true"

print(f"Using endpoint: {endpoint}")
print(f"Using model: {model}")
print(f"Delete resources: {delete_resources}")

project_client = AIProjectClient(endpoint=endpoint, credential=DefaultAzureCredential())
openai_client = project_client.get_openai_client()

with project_client:
    agent = project_client.agents.create_version(
        agent_name="base64-agent",
        definition=PromptAgentDefinition(
            model=model,
            instructions="You are helpful agent"
        )
    )
    print(f"Created agent: {agent.name}:{agent.version}")

    input_message = "Hello, what is in the image ?"
    image_base64 = image_to_base64(asset_file_path)
    data_url = f"data:image/jpeg;base64,{image_base64}"

    response = openai_client.responses.create(
        input=[{
            "role": "user",
            "content": [
                {"type": "input_text", "text": input_message},
                {"type": "input_image", "image_url": data_url}
            ]
        }],
        extra_body={"agent": {"type": "agent_reference", "name": agent.name, "version": agent.version}}
    )
    print(f"Response status: {response.status}")
    if response.error:
        print(f"Error: {response.error}")

    for item in response.output:
        if item.type == "message" and item.content and item.content[0].type == "output_text":
            print(f"assistant: {item.content[0].text}")

    if delete_resources:
        project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
        print("Deleted agent version")
    else:
        print(f"Preserved agent: {agent.name}:{agent.version}")
