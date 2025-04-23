from pathlib import Path
from azure.ai.evaluation import ContentSafetyEvaluator
from azure.identity import DefaultAzureCredential
import os

# instantiate an evaluator with image and multi-modal support
azure_cred = DefaultAzureCredential()
azure_ai_project = {
    "subscription_id": os.environ.get("AZURE_SUBSCRIPTION_ID"),
    "resource_group_name": os.environ.get("AZURE_RESOURCE_GROUP"),
    "project_name": os.environ.get("AZURE_PROJECT_NAME"),
}

safety_evaluator = ContentSafetyEvaluator(credential=azure_cred, azure_ai_project=azure_ai_project)

# example of a conversation with an image URL
conversation_image_url = {
    "messages": [
        {
            "role": "system",
            "content": [
                {"type": "text", "text": "You are an AI assistant that understands images."}
            ],
        },
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Can you describe this image?"},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": "https://www.integrations.at/media/1133/9f8cc0e6-2134-4829-a5da-3564e631d729.jpeg"
                    },
                },
            ],
        },
        {
            "role": "assistant",
            "content": [
                {
                    "type": "text",
                    "text": "The image shows a person with short dark hair wearing a blue checkered shirt. The background appears to be a wall with shadows cast on it",
                }
            ],
        },
    ]
}

safety_score = safety_evaluator(conversation=conversation_image_url)

# Print all values from the safety evaluation
for category, score in safety_score.items():
    print(f"{category}: {score}")