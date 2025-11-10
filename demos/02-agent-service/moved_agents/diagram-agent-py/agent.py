import os
import sys
from dotenv import load_dotenv
from typing import Any
from pathlib import Path
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.agents.models import FilePurpose, CodeInterpreterTool

def main(): 

    # Clear the console
    os.system('cls' if os.name=='nt' else 'clear')

    # Load environment variables from .env file
    load_dotenv()
    endpoint = os.getenv("PROJECT_ENDPOINT")
    model = os.getenv("MODEL_DEPLOYMENT")
    file = os.getenv("DATA_FILE")
    
    print(f"Using endpoint: {endpoint}")
    print(f"Using model: {model}")

    # Display the data to be analyzed
    script_dir = Path(__file__).parent
    
    file_path = script_dir / Path(file)
    print(f"Using data file: {file_path}")

    try:
        with file_path.open('r') as file:
            data = file.read() + "\n"
            print(data)
    except FileNotFoundError:
        print(f"ERROR: Data file not found: {file_path}")
        sys.exit(1)

    # Connect to the Azure AI Foundry project
    agents_client = AIProjectClient(
        endpoint=endpoint,
        credential=DefaultAzureCredential()
    )
    with agents_client:

        # Upload the data file and create a CodeInterpreterTool
        file = agents_client.agents.files.upload_and_poll(
            file_path=file_path, purpose=FilePurpose.AGENTS
        )
        print(f"Uploaded {file.filename}")

        code_interpreter = CodeInterpreterTool(file_ids=[file.id])

        # Define an agent that uses the CodeInterpreterTool
        agent = agents_client.agents.create_agent(
            model=model,
            name="diagram-agent",
            instructions="You are an AI agent that analyzes the data in the file that has been uploaded. If the user requests a chart, create it and save it as a .png file.",
            tools=code_interpreter.definitions,
            tool_resources=code_interpreter.resources,
        )
        print(f"Using agent: {agent.name}")

        # Create a thread for the conversation
        thread = agents_client.agents.create_thread()
        
        # Loop until the user types 'quit'
        while True:
            # Get input text
            user_prompt = input("Enter a prompt (or type 'quit' to exit): ")
            if user_prompt.lower() == "quit":
                break
            if len(user_prompt) == 0:
                print("Please enter a prompt.")
                continue

            # Send a prompt to the agent
            message = agents_client.agents.create_message(
                thread_id=thread.id,
                role="user",
                content=user_prompt,
            )

            run = agents_client.agents.create_and_process_run(thread_id=thread.id, agent_id=agent.id)

            # Check the run status for failures
            if run.status == "failed":
                print(f"Run failed: {run.last_error}")
    
            # Show the latest response from the agent
            messages = agents_client.agents.list_messages(thread_id=thread.id)
            last_msg = messages.get_last_text_message_by_role("assistant")
            if last_msg:
                print(f"Last Message: {last_msg.text.value}")

            # Get the conversation history
            print("\nConversation Log:\n")
            messages = agents_client.agents.list_messages(thread_id=thread.id)
            for message_data in reversed(messages.data):
                last_message_content = message_data.content[-1]
                print(f"{message_data.role}: {last_message_content.text.value}\n")

            # Get any generated files
            for file_path_annotation in messages.file_path_annotations:
                agents_client.agents.save_file(file_id=file_path_annotation.file_path.file_id, file_name=Path(file_path_annotation.text).name)
                print(f"File saved as {Path(file_path_annotation.text).name}")


        # Clean up
        agents_client.agents.delete_agent(agent.id)
        agents_client.agents.delete_thread(thread.id)



        # Clean up
        agents_client.agents.delete_agent(agent.id)
        agents_client.agents.delete_thread(thread.id)

if __name__ == '__main__': 
    main()