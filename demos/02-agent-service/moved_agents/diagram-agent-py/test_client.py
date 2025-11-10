import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

load_dotenv()
endpoint = os.getenv('AZURE_AI_AGENT_ENDPOINT')
print(f'Endpoint: {endpoint}')

try:
    project_client = AIProjectClient(
        endpoint=endpoint,
        credential=DefaultAzureCredential(exclude_environment_credential=True, exclude_managed_identity_credential=True)
    )
    print('AIProjectClient created successfully')
except Exception as e:
    print(f'Failed to create AIProjectClient: {e}')