from azure.ai.projects.aio import AIProjectClient
from azure.ai.projects.models import (
    Agent,
    AgentThread,
    AsyncFunctionTool,
    AsyncToolSet,
    BingGroundingTool,
    CodeInterpreterTool,
    FileSearchTool,
)
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

load_dotenv()

project_client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(),
    conn_str=PROJECT_CONNECTION_STRING,
)

agent = project_client.create_agent(
    model = MODEL_DEPLOYMENT_NAME,
    agent_name = "AZ Function Agent",
    instructions = "You are a helpful agent that is knowledgeable about Currency Conversion",
    headers={"x-ms-enable-preview": "true"},
    tools=[
        {
            "type": "azure_function",
            "azure_function": {
                "function": {
                    "name": "convertTo",
                    "description": "Converts a currency to another currency.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "from": {"type": "string", "description": "The currency code to convert from (e.g., EUR)."},
                            "to": {"type": "string", "description": "The currency code to convert to (e.g., THB)."},
                            "amount": {"type": "number", "description": "The amount of currency to convert."}
                        },
                        "required": ["from", "to", "amount"]
                    }
                }
            }
        }
    ],
)

thread = project_client.agents.create_thread()
print(f"Created thread, thread ID: {thread.id}")

# Send the prompt to the agent
message = project_client.agents.create_message(
    thread_id=thread.id,
    role="user",
    content="How much is 1000 EUR in THB?"
)
print(f"Created message, message ID: {message.id}")

# Run the agent
run = project_client.agents.create_run(thread_id=thread.id, agent_id=agent.id)
# Monitor and process the run status. The function call should be placed on the input queue by the Agent Service for the Azure Function to pick up when requires_action is returned
while run.status in ["queued", "in_progress", "requires_action"]:
    time.sleep(1)
    run = project_client.agents.get_run(thread_id=thread.id, run_id=run.id)

    if run.status not in ["queued", "in_progress", "requires_action"]:
        break

print(f"Run finished with status: {run.status}")

# Get messages from the assistant thread
messages = project_client.agents.get_messages(thread_id=thread.id)
print(f"Messages: {messages}")

# Get the last message from the assistant
last_msg = messages.get_last_text_message_by_sender("assistant")
if last_msg:
    print(f"Last Message: {last_msg.text.value}")

# Delete the agent once done
project_client.agents.delete_agent(agent.id)
print("Deleted agent")