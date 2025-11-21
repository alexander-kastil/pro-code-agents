import json
import os
import io
import sys

from azure.ai.agents.models import OpenApiAnonymousAuthDetails, OpenApiTool
from azure.ai.agents import AgentsClient
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

# Configure UTF-8 encoding for Windows console (fixes emoji display issues)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Detailed logging flag
DETAILED_LOGGING = True


def log(message: str) -> None:
    """Print log message if detailed logging is enabled."""
    if DETAILED_LOGGING:
        print(f"[LOG] {message}")


def main() -> None:
    try:
        os.system("cls" if os.name == "nt" else "clear")
        load_dotenv()

        endpoint = os.getenv("PROJECT_ENDPOINT")
        model = os.getenv("MODEL_DEPLOYMENT")
        rest_url = os.getenv("REST_URL")

        log(f"Using endpoint: {endpoint}")
        log(f"Using model: {model}")
        log(f"REST API URL: {rest_url}")

        # Define the OpenAPI specification for the Food Catalog API
        openapi_spec = {
            "openapi": "3.0.4",
            "info": {
                "title": "Food-Inventory",
                "version": "v1"
            },
            "servers": [
                {
                    "url": f"https://{rest_url}"
                }
            ],
            "paths": {
                "/Food": {
                    "get": {
                        "operationId": "getAllFood",
                        "tags": ["Food"],
                        "summary": "Get all food items",
                        "responses": {
                            "200": {
                                "description": "OK",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "array",
                                            "items": {
                                                "$ref": "#/components/schemas/FoodItem"
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "post": {
                        "operationId": "addFood",
                        "tags": ["Food"],
                        "summary": "Add a new food item",
                        "requestBody": {
                            "required": True,
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/FoodDTO"
                                    }
                                }
                            }
                        },
                        "responses": {
                            "200": {
                                "description": "OK",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "$ref": "#/components/schemas/FoodItem"
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "components": {
                "schemas": {
                    "FoodDTO": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "nullable": True
                            },
                            "price": {
                                "type": "number",
                                "format": "double"
                            },
                            "inStock": {
                                "type": "integer",
                                "format": "int32"
                            },
                            "minStock": {
                                "type": "integer",
                                "format": "int32"
                            },
                            "pictureUrl": {
                                "type": "string",
                                "nullable": True
                            },
                            "description": {
                                "type": "string",
                                "nullable": True
                            }
                        },
                        "additionalProperties": False
                    },
                    "FoodItem": {
                        "type": "object",
                        "properties": {
                            "id": {
                                "type": "integer",
                                "format": "int32"
                            },
                            "name": {
                                "type": "string",
                                "nullable": True
                            },
                            "price": {
                                "type": "number",
                                "format": "double"
                            },
                            "inStock": {
                                "type": "integer",
                                "format": "int32"
                            },
                            "minStock": {
                                "type": "integer",
                                "format": "int32"
                            },
                            "pictureUrl": {
                                "type": "string",
                                "nullable": True
                            },
                            "description": {
                                "type": "string",
                                "nullable": True
                            }
                        },
                        "additionalProperties": False
                    }
                }
            }
        }

        log("Created OpenAPI specification")

        project_client = AIProjectClient(
            endpoint=endpoint,
            credential=DefaultAzureCredential(),
        )
        log("Created AIProjectClient")

        agents_client = AgentsClient(
            endpoint=endpoint,
            credential=DefaultAzureCredential(),
        )
        log("Created AgentsClient")

        # Create OpenAPI tool with anonymous authentication
        auth = OpenApiAnonymousAuthDetails()
        openapi_tool = OpenApiTool(
            name="food_catalog_api",
            spec=openapi_spec,
            description="Access the Food Catalog API to manage food inventory",
            auth=auth
        )
        log("Created OpenApiTool with anonymous authentication")

        with agents_client:
            agent = agents_client.create_agent(
                model=model,
                name="food-catalog-agent",
                instructions=(
                    "You are a helpful assistant that helps manage a food catalog inventory. "
                    "You can retrieve food items and add new items to the catalog. "
                    "When adding food, use realistic data for the fields. "
                    "Always confirm the results of operations to the user."
                ),
                description="Demonstrates calling REST APIs using OpenAPI 3.0 specification for food inventory management.",
                tools=openapi_tool.definitions
            )
            log(f"Created agent: {agent.name} ({agent.id})")

            thread = agents_client.threads.create()
            log(f"Created thread: {thread.id}")
            
            print(f"\n{'='*70}")
            print(f"🍔 Food Catalog Management Agent")
            print(f"Agent: {agent.name} ({agent.id})")
            print(f"{'='*70}\n")

            # Step 1: Get all food items initially
            print(f"{'─'*70}")
            print("📋 Step 1: Retrieving current food inventory...")
            print(f"{'─'*70}\n")
            
            input("Press Enter to continue...")
            print()

            message = agents_client.messages.create(
                thread_id=thread.id,
                role="user",
                content="Please get all food items from the catalog and show them in a nice format."
            )
            log(f"Created message: {message['id'] if isinstance(message, dict) else message.id}")
            
            log("Creating and processing run...")
            run = agents_client.runs.create_and_process(
                thread_id=thread.id,
                agent_id=agent.id
            )
            log(f"Run completed with status: {run.status}")

            if run.status == "failed":
                print(f"\n❌ Error: {run.last_error}\n")
                log(f"Run error details: {run.last_error}")
            else:
                messages = agents_client.messages.list(thread_id=thread.id)
                log(f"Retrieved messages from thread")
                
                for message in messages:
                    if message.role == "assistant":
                        if isinstance(message.content, list) and len(message.content) > 0:
                            if message.content[0].get('type') == 'text':
                                assistant_text = message.content[0]['text']['value']
                                log(f"Assistant response: {assistant_text}")
                                print(f"✅ Current Inventory:\n{assistant_text}\n")
                        else:
                            log(f"Assistant message: {message.content}")
                            print(f"\n✅ Result: {message.content}\n")
                        break

            # Step 2: Add a new food item
            print(f"\n{'─'*70}")
            print("➕ Step 2: Adding a new food item to the catalog...")
            print(f"{'─'*70}\n")
            
            input("Press Enter to continue...")
            print()

            message = agents_client.messages.create(
                thread_id=thread.id,
                role="user",
                content=(
                    "Please add a new food item to the catalog. "
                    "Create a pizza with creative details (name, price around 12.99, "
                    "stock around 25, minimum stock 5, and an interesting description)."
                )
            )
            log(f"Created message: {message['id'] if isinstance(message, dict) else message.id}")
            
            log("Creating and processing run...")
            run = agents_client.runs.create_and_process(
                thread_id=thread.id,
                agent_id=agent.id
            )
            log(f"Run completed with status: {run.status}")

            if run.status == "failed":
                print(f"\n❌ Error: {run.last_error}\n")
                log(f"Run error details: {run.last_error}")
            else:
                messages = agents_client.messages.list(thread_id=thread.id)
                log(f"Retrieved messages from thread")
                
                for message in messages:
                    if message.role == "assistant":
                        if isinstance(message.content, list) and len(message.content) > 0:
                            if message.content[0].get('type') == 'text':
                                assistant_text = message.content[0]['text']['value']
                                log(f"Assistant response: {assistant_text}")
                                print(f"✅ Food Item Added:\n{assistant_text}\n")
                        else:
                            log(f"Assistant message: {message.content}")
                            print(f"\n✅ Result: {message.content}\n")
                        break

            # Step 3: Get all food items again to see the new item
            print(f"\n{'─'*70}")
            print("📋 Step 3: Retrieving updated food inventory...")
            print(f"{'─'*70}\n")
            
            input("Press Enter to continue...")
            print()

            message = agents_client.messages.create(
                thread_id=thread.id,
                role="user",
                content="Please get all food items again to show the updated catalog."
            )
            log(f"Created message: {message['id'] if isinstance(message, dict) else message.id}")
            
            log("Creating and processing run...")
            run = agents_client.runs.create_and_process(
                thread_id=thread.id,
                agent_id=agent.id
            )
            log(f"Run completed with status: {run.status}")

            if run.status == "failed":
                print(f"\n❌ Error: {run.last_error}\n")
                log(f"Run error details: {run.last_error}")
            else:
                messages = agents_client.messages.list(thread_id=thread.id)
                log(f"Retrieved messages from thread")
                
                for message in messages:
                    if message.role == "assistant":
                        if isinstance(message.content, list) and len(message.content) > 0:
                            if message.content[0].get('type') == 'text':
                                assistant_text = message.content[0]['text']['value']
                                log(f"Assistant response: {assistant_text}")
                                print(f"✅ Updated Inventory:\n{assistant_text}\n")
                        else:
                            log(f"Assistant message: {message.content}")
                            print(f"\n✅ Result: {message.content}\n")
                        break

            delete_on_exit = os.getenv("DELETE_AGENT_ON_EXIT", "true").lower() == "true"
            if delete_on_exit:
                agents_client.delete_agent(agent.id)
                log(f"Deleted agent: {agent.id}")
                print(f"\n{'='*70}")
                print("🗑️  Agent deleted successfully")
                print(f"{'='*70}\n")
            else:
                log(f"Agent {agent.id} preserved for examination")
                print(f"\n{'='*70}")
                print(f"💾  Agent {agent.id} preserved for examination in Azure AI Foundry")
                print(f"{'='*70}\n")
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user. Exiting gracefully...")
        log("User interrupted with Ctrl+C")
    except Exception as e:
        print(f"\n❌ Error: {type(e).__name__}: {e}")
        if DETAILED_LOGGING:
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()

