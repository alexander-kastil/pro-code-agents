import os
import time
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.agents.models import ListSortOrder
import qrcode
import io
from datetime import datetime
from azure.storage.blob import BlobServiceClient

def main():

    # Clear the console to keep the output focused on the agent interaction
    os.system('cls' if os.name == 'nt' else 'clear')

    # Load environment variables from .env file
    load_dotenv()
    endpoint = os.getenv("PROJECT_ENDPOINT")
    model = os.getenv("MODEL_DEPLOYMENT")
    storage_connection_string = os.getenv("STORAGE_CONNECTION_STRING")
    storage_account_name = os.getenv("STORAGE_ACCOUNT_NAME")
    storage_container_name = os.getenv("STORAGE_CONTAINER_NAME")

    print(f"Using endpoint: {endpoint}")
    print(f"Using model: {model}")

    # Connect to the Azure AI Foundry project
    agents_client = AIProjectClient(
        endpoint=endpoint,
        credential=DefaultAzureCredential()
    )
    with agents_client:

        agent = agents_client.agents.create_agent(
            model=model,
            name="basic-agent",
            instructions="You are helpful agent"
        )

        print(f"Created agent: {agent.name}, ID: {agent.id}")

        # Create a thread for the conversation
        thread = agents_client.agents.threads.create()
        print(f"Created thread, thread ID: {thread.id}")

        # [START create_message]
        message = agents_client.agents.messages.create(
            thread_id=thread.id,
            role="user",
            content="Hello"
        )
        # [END create_message]
        print(f"Created message, message ID: {message.id}")

        # [START create_run]
        run = agents_client.agents.runs.create(thread_id=thread.id, agent_id=agent.id)

        # Poll the run as long as run status is queued or in progress
        while run.status in ["queued", "in_progress", "requires_action"]:
            # Wait for a second between status checks
            time.sleep(1)
            run = agents_client.agents.runs.get(thread_id=thread.id, run_id=run.id)
            # [END create_run]
            print(f"Run status: {run.status}")

        if run.status == "failed":
            print(f"Run error: {run.last_error}")

        agents_client.agents.delete_agent(agent.id)
        print("Deleted agent")

        # [START list_messages]
        messages = agents_client.agents.messages.list(
            thread_id=thread.id,
            order=ListSortOrder.ASCENDING
        )
        agent_response = ""
        for msg in messages:
            if msg.text_messages:
                last_text = msg.text_messages[-1]
                print(f"{msg.role}: {last_text.text.value}")
                if msg.role == "assistant":
                    agent_response = last_text.text.value
        # [END list_messages]

        # Ask for QR code content
        user_input = input("What do you want to encode? Press Enter for default: https://www.integrations.at\n")
        qr_content = user_input if user_input.strip() else "https://www.integrations.at"

        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(qr_content)
        qr.make(fit=True)
        img = qr.make_image(fill='black', back_color='white')

        # Save to bytes
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)

        # Upload to blob storage
        date_str = datetime.now().strftime("%Y%m%d")
        blob_name = f"qr{date_str}.jpg"

        blob_service_client = BlobServiceClient.from_connection_string(storage_connection_string)
        container_client = blob_service_client.get_container_client(storage_container_name)
        try:
            container_client.create_container()
            print(f"Created container {storage_container_name}")
        except Exception as e:
            if "ContainerAlreadyExists" not in str(e):
                raise
        blob_client = blob_service_client.get_blob_client(container=storage_container_name, blob=blob_name)
        blob_client.upload_blob(img_bytes, overwrite=True)

        # Get download URL
        download_url = f"https://procodestorageacct.blob.core.windows.net/{storage_container_name}/{blob_name}"
        print(f"QR Code uploaded. Download URL: {download_url}")


if __name__ == '__main__':
    main()
