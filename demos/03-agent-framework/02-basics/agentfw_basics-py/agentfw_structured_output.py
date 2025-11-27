import os
import json
from pydantic import BaseModel
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition

# Load environment variables
load_dotenv()

endpoint = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
model = os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME", "gpt-4o")
delete_resources = os.getenv("DELETE", "true").lower() == "true"


# Define structured output model
class PersonInfo(BaseModel):
    """Extract person information from text."""
    name: str | None = None
    age: int | None = None
    occupation: str | None = None
    city: str | None = None


def main():
    """Interactive demo: Structured output extraction using Foundry."""
    
    print("\n" + "="*70)
    print("DEMO: Structured Output with Pydantic (Foundry)")
    print("="*70)
    
    # Initialize project client and OpenAI responses client
    project_client = AIProjectClient(endpoint=endpoint, credential=DefaultAzureCredential())
    openai_client = project_client.get_openai_client()
    
    with project_client:
        # Create agent with JSON output instructions
        agent = project_client.agents.create_version(
            agent_name="extractor-bot",
            definition=PromptAgentDefinition(
                model=model,
                instructions="""Extract person information from the user's text.
ALWAYS respond with a JSON object containing these fields:
{
    "name": "string or null",
    "age": "number or null",
    "occupation": "string or null",
    "city": "string or null"
}
Return ONLY the JSON object, no markdown code blocks or extra text."""
            )
        )
        
        print(f"\nAgent created: {agent.name} (version {agent.version})")
        print("Schema: name, age, occupation, city")
        
        print("\n" + "="*70)
        print("Interactive Chat (Type 'quit' to exit)")
        print("="*70)
        print("\nTIP: Describe a person and see structured extraction")
        print("Example: 'John is a 35 year old software engineer from Seattle'\n")
        
        while True:
            try:
                user_input = input("You: ")
            except EOFError:
                print("\nReceived EOF - exiting.")
                break
            except KeyboardInterrupt:
                print("\nInterrupted - exiting.")
                break
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\nGoodbye!")
                break
            
            if not user_input.strip():
                continue
            
            # Get response from agent
            print("\nExtracting structured data...")
            response = openai_client.responses.create(
                input=[{"role": "user", "content": user_input}],
                extra_body={"agent": {"type": "agent_reference", "name": agent.name, "version": agent.version}}
            )
            
            # Process response
            if response.status == "completed":
                for item in response.output:
                    if item.type == "message" and item.content and item.content[0].type == "output_text":
                        response_text = item.content[0].text.strip()
                        
                        # Try to parse as JSON and validate with Pydantic
                        try:
                            # Clean up potential markdown code blocks
                            json_text = response_text
                            if json_text.startswith("```"):
                                json_text = json_text.split("```")[1]
                                if json_text.startswith("json"):
                                    json_text = json_text[4:]
                                json_text = json_text.strip()
                            
                            # Parse JSON and validate with Pydantic
                            data = json.loads(json_text)
                            person = PersonInfo(**data)
                            
                            print("\nExtracted Information:")
                            print(f"   Name: {person.name}")
                            print(f"   Age: {person.age}")
                            print(f"   Occupation: {person.occupation}")
                            print(f"   City: {person.city}")
                        except json.JSONDecodeError:
                            print(f"\nRaw response (not JSON): {response_text}")
                        except Exception as e:
                            print(f"\nValidation error: {e}")
                            print(f"Raw response: {response_text}")
            else:
                print(f"Response failed: {response.status}")
                if response.error:
                    print(f"Error: {response.error}")
            
            print()
        
        # Cleanup based on DELETE flag
        if delete_resources:
            project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
            print("Deleted agent version")
        else:
            print(f"Agent preserved: {agent.name}:{agent.version}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nSee you again soon.")
