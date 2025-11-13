"""
REST API Tool Demo - Food Catalog API

This demo shows how to create custom tools that call external REST APIs.
We'll use the Food Catalog API to demonstrate querying food items.

API: https://food-catalog-api-dev.azurewebsites.net
Swagger: https://food-catalog-api-dev.azurewebsites.net/swagger/v1/swagger.json
"""

import asyncio
import os
from typing import Annotated, Optional
from pydantic import Field
from dotenv import load_dotenv
import requests

from agent_framework.azure import AzureOpenAIChatClient

# Load environment variables
load_dotenv()

ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
DEPLOYMENT = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME")
API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-07-01-preview")

# Food Catalog API base URL
FOOD_API_BASE = "https://food-catalog-api-dev.azurewebsites.net"


# Define REST API tools
def get_food_items(
    category: Annotated[Optional[str], Field(description="Food category to filter by (e.g., 'fruits', 'vegetables', 'dairy')")] = None,
    search: Annotated[Optional[str], Field(description="Search term to find food items")] = None
) -> str:
    """Get food items from the catalog, optionally filtered by category or search term."""
    try:
        params = {}
        if category:
            params['category'] = category
        if search:
            params['search'] = search
        
        response = requests.get(
            f"{FOOD_API_BASE}/api/foods",
            params=params,
            timeout=10
        )
        
        if response.status_code == 200:
            items = response.json()
            if not items:
                return "No food items found."
            
            result = "Food Items:\n"
            for item in items[:10]:  # Limit to 10 items
                name = item.get('name', 'Unknown')
                cat = item.get('category', 'N/A')
                price = item.get('price', 'N/A')
                result += f"- {name} ({cat}) - ${price}\n"
            
            if len(items) > 10:
                result += f"\n... and {len(items) - 10} more items"
            
            return result
        else:
            return f"Error: API returned status {response.status_code}"
    except requests.exceptions.Timeout:
        return "Error: Request timed out. The API might be unavailable."
    except requests.exceptions.RequestException as e:
        return f"Error: Could not connect to Food Catalog API - {str(e)}"


def get_food_details(
    food_id: Annotated[int, Field(description="The ID of the food item to get details for")]
) -> str:
    """Get detailed information about a specific food item by ID."""
    try:
        response = requests.get(
            f"{FOOD_API_BASE}/api/foods/{food_id}",
            timeout=10
        )
        
        if response.status_code == 200:
            item = response.json()
            result = f"Food Details:\n"
            result += f"Name: {item.get('name', 'Unknown')}\n"
            result += f"Category: {item.get('category', 'N/A')}\n"
            result += f"Price: ${item.get('price', 'N/A')}\n"
            result += f"Description: {item.get('description', 'No description')}\n"
            result += f"Calories: {item.get('calories', 'N/A')}\n"
            result += f"In Stock: {item.get('inStock', 'Unknown')}\n"
            return result
        elif response.status_code == 404:
            return f"Food item with ID {food_id} not found."
        else:
            return f"Error: API returned status {response.status_code}"
    except requests.exceptions.Timeout:
        return "Error: Request timed out. The API might be unavailable."
    except requests.exceptions.RequestException as e:
        return f"Error: Could not connect to Food Catalog API - {str(e)}"


def get_food_categories() -> str:
    """Get all available food categories from the catalog."""
    try:
        response = requests.get(
            f"{FOOD_API_BASE}/api/categories",
            timeout=10
        )
        
        if response.status_code == 200:
            categories = response.json()
            if not categories:
                return "No categories found."
            
            result = "Available Food Categories:\n"
            for cat in categories:
                result += f"- {cat}\n"
            return result
        else:
            return f"Error: API returned status {response.status_code}"
    except requests.exceptions.Timeout:
        return "Error: Request timed out. The API might be unavailable."
    except requests.exceptions.RequestException as e:
        return f"Error: Could not connect to Food Catalog API - {str(e)}"


async def main():
    """Interactive demo: Agent with REST API tools."""
    
    print("\n" + "="*70)
    print("🍎 DEMO: REST API Tools - Food Catalog")
    print("="*70)
    print(f"""
This demo shows how to create custom tools that call REST APIs.

API: {FOOD_API_BASE}

Available Tools:
1. get_food_items - Browse food catalog with optional filters
2. get_food_details - Get detailed info about a food item
3. get_food_categories - List all food categories

Example queries:
- "Show me all fruits"
- "What vegetables are available?"
- "Get details for food item 5"
- "What categories are available?"
- "Find food items with 'apple' in the name"
    """)
    
    # Create agent with REST API tools
    agent = AzureOpenAIChatClient(
        endpoint=ENDPOINT,
        deployment_name=DEPLOYMENT,
        api_key=API_KEY,
        api_version=API_VERSION
    ).create_agent(
        instructions=(
            "You are a helpful assistant with access to a food catalog API. "
            "Use the tools to help users find food items, get details, and browse categories. "
            "Always provide clear and helpful responses. "
            "If the API is unavailable, inform the user politely and suggest trying again later."
        ),
        name="FoodCatalogBot",
        tools=[get_food_items, get_food_details, get_food_categories]
    )
    
    print("\n✅ Agent created with REST API tools")
    
    print("\n" + "="*70)
    print("💬 Interactive Chat (Type 'quit' to exit)")
    print("="*70 + "\n")
    
    while True:
        try:
            user_input = input("You: ")
        except EOFError:
            print("\n👋 Received EOF - exiting.")
            break
        except KeyboardInterrupt:
            print("\n👋 Interrupted - exiting.")
            break
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("\n👋 Goodbye!")
            break
        
        if not user_input.strip():
            continue
        
        print("Agent: ", end="", flush=True)
        async for chunk in agent.run_stream(user_input):
            if chunk.text:
                print(chunk.text, end="", flush=True)
        print("\n")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 See you again soon.")
