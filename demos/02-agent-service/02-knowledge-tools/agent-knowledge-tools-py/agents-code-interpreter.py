import os
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.ai.agents.models import CodeInterpreterTool
from azure.ai.agents.models import FilePurpose, MessageAttachment, MessageRole
from azure.identity import DefaultAzureCredential
from pathlib import Path

def main():
    # Clear the console to keep the output focused on the agent interaction
    os.system('cls' if os.name == 'nt' else 'clear')

    # Load environment variables from .env file
    load_dotenv()
    endpoint = os.getenv("PROJECT_ENDPOINT")
    model = os.getenv("MODEL_DEPLOYMENT")

    print(f"Using endpoint: {endpoint}")
    print(f"Using model: {model}")

    asset_file_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "assets", "quarterly_results.csv")
    )

    project_client = AIProjectClient(
        endpoint=endpoint,
        credential=DefaultAzureCredential(),
    )

    with project_client:
        agents_client = project_client.agents
        # Upload a file and wait for it to be processed
        # [START upload_file_and_create_agent_with_code_interpreter]
        file = agents_client.files.upload_and_poll(file_path=asset_file_path, purpose=FilePurpose.AGENTS)
        print(f"Uploaded file, file ID: {file.id}")

        code_interpreter = CodeInterpreterTool(file_ids=[file.id])

        # Create agent with code interpreter tool and tools_resources
        agent = agents_client.create_agent(
            model=model,
            name="code-interpreter-agent",
            instructions="You are a helpful agent with access to code interpreter tools. Use the code interpreter to analyze the uploaded CSV file and create visualizations. The sector is in column 'sector' and the operating profit is in column 'operating_profit'. Build a bar chart for the operating profit and provide the file to the user as a downloadable link.",
            tools=code_interpreter.definitions,
            tool_resources=code_interpreter.resources,
        )
        # [END upload_file_and_create_agent_with_code_interpreter]
        print(f"Created agent, agent ID: {agent.id}")

        thread = agents_client.threads.create()
        print(f"Created thread, thread ID: {thread.id}")

        # Create a message
        message = agents_client.messages.create(
            thread_id=thread.id,
            role="user",
            content="Could you please create bar chart in TRANSPORTATION sector for the operating profit from the uploaded csv file and provide file to me?",
            attachments=[
                MessageAttachment(
                    file_id=file.id,
                    tools=code_interpreter.definitions,
                )
            ],
        )
        print(f"Created message, message ID: {message.id}")

        run = agents_client.runs.create_and_process(thread_id=thread.id, agent_id=agent.id)
        print(f"Run finished with status: {run.status}")

        if run.status == "failed":
            # Check if you got "Rate limit is exceeded.", then you want to get more quota
            print(f"Run failed: {run.last_error}")

        # [START get_messages_and_save_files]
        messages = agents_client.messages.list(thread_id=thread.id)
        print(f"Messages: {messages}")

        for msg in messages:
            # Save every image file in the message
            for img in msg.image_contents:
                file_id = img.image_file.file_id
                file_name = f"{file_id}_image_file.png"
                agents_client.files.save(file_id=file_id, file_name=file_name)
                print(f"Saved image file to: {Path.cwd() / file_name}")

            # Print details of every file-path annotation
            for ann in msg.file_path_annotations:
                print("File Paths:")
                print(f"  Type: {ann.type}")
                print(f"  Text: {ann.text}")
                print(f"  File ID: {ann.file_path.file_id}")
                print(f"  Start Index: {ann.start_index}")
                print(f"  End Index: {ann.end_index}")
        # [END get_messages_and_save_files]

        last_msg = agents_client.messages.get_last_message_text_by_role(thread_id=thread.id, role=MessageRole.AGENT)
        if last_msg:
            print(f"Last Message: {last_msg.text.value}")

        agents_client.files.delete(file.id)
        print("Deleted file")

        agents_client.delete_agent(agent.id)
        print("Deleted agent")


if __name__ == '__main__':
    main()
