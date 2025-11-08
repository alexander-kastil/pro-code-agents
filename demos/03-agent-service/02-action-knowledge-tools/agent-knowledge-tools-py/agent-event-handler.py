import os
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from typing import Any, Optional
from azure.ai.agents.models import (
    AgentEventHandler,
    ListSortOrder,
    MessageDeltaChunk,
    ThreadMessage,
    ThreadRun,
    RunStep,
)

# Clear the console to keep the output focused on the agent interaction
os.system('cls' if os.name == 'nt' else 'clear')

# Load environment variables from .env file
load_dotenv()
endpoint = os.getenv("PROJECT_ENDPOINT")
model = os.getenv("MODEL_DEPLOYMENT")

agents_client = AIProjectClient(
    endpoint=endpoint,
    credential=DefaultAzureCredential(),
)


# [START stream_event_handler]
# With AgentEventHandler[str], the return type for each event functions is optional string.
class MyEventHandler(AgentEventHandler[str]):

    def on_message_delta(self, delta: "MessageDeltaChunk") -> Optional[str]:
        return f"Text delta received: {delta.text}"

    def on_thread_message(self, message: "ThreadMessage") -> Optional[str]:
        return f"ThreadMessage created. ID: {message.id}, Status: {message.status}"

    def on_thread_run(self, run: "ThreadRun") -> Optional[str]:
        return f"ThreadRun status: {run.status}"

    def on_run_step(self, step: "RunStep") -> Optional[str]:
        return f"RunStep type: {step.type}, Status: {step.status}"

    def on_error(self, data: str) -> Optional[str]:
        return f"An error occurred. Data: {data}"

    def on_done(self) -> Optional[str]:
        return "Stream completed."

    def on_unhandled_event(self, event_type: str, event_data: Any) -> Optional[str]:
        return f"Unhandled Event Type: {event_type}, Data: {event_data}"


# [END stream_event_handler]


with agents_client:

    # Create an agent and run stream with event handler
    agent = agents_client.create_agent(
        model=model, name="event-handler-agent", instructions="You are a helpful agent"
    )
    
    print(f"Created agent: {agent.name}, ID: {agent.id}")

    # Create a thread for the conversation
    thread = agents_client.threads.create()
    print(f"Created thread, thread ID {thread.id}")

    message = agents_client.messages.create(thread_id=thread.id, role="user", content="Hello, tell me a joke")
    print(f"Created message, message ID {message.id}")

    # [START create_stream]
    with agents_client.runs.stream(thread_id=thread.id, agent_id=agent.id, event_handler=MyEventHandler()) as stream:
        for event_type, event_data, func_return in stream:
            print(f"Received data.")
            print(f"Streaming receive Event Type: {event_type}")
            print(f"Event Data: {str(event_data)[:100]}...")
            print(f"Event Function return: {func_return}\n")
    # [END create_stream]

    agents_client.delete_agent(agent.id)
    print("Deleted agent")

    messages = agents_client.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)
    for msg in messages:
        if msg.text_messages:
            last_text = msg.text_messages[-1]
            print(f"{msg.role}: {last_text.text.value}")
