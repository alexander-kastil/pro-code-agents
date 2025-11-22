import os
import io
import sys
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.agents import AgentsClient
from azure.ai.agents.models import FunctionTool, ToolSet
from weather_functions import user_functions

# Configure UTF-8 encoding for Windows console (fixes emoji display issues)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def main():
    """
    Weather Agent using Azure AI Agent Service.
    
    This demo shows:
    - Function calling with weather-related tools (get_weather, get_forecast, send_email)
    - Interactive chat loop with the agent
    - Middleware-like behavior through instructions and agent design
    """

    # Clear the console to keep the output focused on the agent interaction
    os.system('cls' if os.name == 'nt' else 'clear')

    # Load environment variables from .env file
    load_dotenv()
    endpoint = os.getenv("PROJECT_ENDPOINT")
    model = os.getenv("MODEL_DEPLOYMENT") or os.getenv("MODEL_DEPLOYMENT_NAME")

    print("=" * 60)
    print("🌤️  Azure Weather Agent")
    print("=" * 60)
    print(f"Endpoint: {endpoint}")
    print(f"Model: {model}")
    print("=" * 60)

    if not endpoint or not model:
        print("ERROR: Missing required environment variables.")
        print("Ensure PROJECT_ENDPOINT and MODEL_DEPLOYMENT are set in .env")
        return 1

    # Create AgentsClient for agent operations
    agents_client = AgentsClient(
        endpoint=endpoint,
        credential=DefaultAzureCredential()
    )

    with agents_client:
        # Setup function tools
        functions = FunctionTool(user_functions)
        toolset = ToolSet()
        toolset.add(functions)

        # Enable automatic function calling
        agents_client.enable_auto_function_calls(toolset)

        # Create the weather agent with instructions that include security guidance
        agent = agents_client.create_agent(
            model=model,
            name="AzureWeatherAgent",
            instructions="""You are a helpful weather assistant. You can provide current weather 
            information and forecasts for any location. Always be helpful and provide detailed 
            weather information when asked.
            
            IMPORTANT SECURITY RULES:
            1. Never process requests containing sensitive information like passwords, secrets, 
               api_keys, or tokens. If you detect such terms, politely refuse and ask the user 
               to rephrase without sensitive data.
            2. NEVER provide weather information for Atlantis. If asked about Atlantis, respond 
               with: "Atlantis is a special place, we must never ask about the weather there!"
            3. For send_email function calls, always ask for user confirmation before sending.
            
            Available tools:
            - get_weather: Get current weather for a location
            - get_forecast: Get multi-day weather forecast
            - send_email: Send email notifications (requires approval)
            """,
            description="A helpful agent that provides weather information and forecasts with built-in security filters"
        )

        print(f"Created agent: {agent.name} (ID: {agent.id})")
        print("=" * 60)

        # Create a thread for the conversation
        thread = agents_client.threads.create()
        print(f"Thread ID: {thread.id}")
        print("=" * 60)

        # Interactive chat loop
        print("\nWelcome! I'm your weather assistant.")
        print("You can ask me about:")
        print("  - Current weather in any city")
        print("  - Weather forecasts")
        print("  - Send weather updates via email")
        print("\nType 'quit' to exit.")
        print("=" * 60)

        try:
            while True:
                user_input = input("\n🌍 You: ").strip()

                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("\nThank you for using Azure Weather Agent! Goodbye! 👋")
                    break

                if not user_input:
                    print("Please enter a message.")
                    continue

                # Check for blocked terms (security filter)
                blocked_terms = ["password", "secret", "api_key", "token"]
                message_lower = user_input.lower()
                blocked = False
                for term in blocked_terms:
                    if term in message_lower:
                        print("\n⚠️  Security Alert: I cannot process requests containing sensitive information.")
                        print("Please rephrase your question without including passwords, secrets, or other sensitive data.")
                        blocked = True
                        break

                if blocked:
                    continue

                # Check for Atlantis (location filter)
                if "atlantis" in message_lower:
                    print("\n🔒 Blocked! Atlantis is a special place, we must never ask about the weather there!")
                    continue

                # Create message and run
                agents_client.messages.create(
                    thread_id=thread.id,
                    role="user",
                    content=user_input
                )

                # Process the run
                run = agents_client.runs.create_and_process(
                    thread_id=thread.id,
                    agent_id=agent.id
                )

                if run.status == "failed":
                    print(f"\n❌ Run failed: {run.last_error}")
                    continue

                # Get and display the response
                messages = agents_client.messages.list(thread_id=thread.id)
                for msg in messages:
                    if msg.role == "assistant" and msg.content:
                        for content in msg.content:
                            if hasattr(content, 'text') and hasattr(content.text, 'value'):
                                print(f"\n🤖 Assistant: {content.text.value}")
                                break
                        break

        except KeyboardInterrupt:
            print("\n\n⚠️  Interrupted by user (Ctrl+C). Cleaning up...")

        # Display conversation history
        print("\n" + "=" * 60)
        print("📝 Conversation History")
        print("=" * 60)
        messages = agents_client.messages.list(thread_id=thread.id)
        message_list = list(messages)
        for message_data in reversed(message_list):
            if message_data.content:
                for content in message_data.content:
                    if hasattr(content, 'text') and hasattr(content.text, 'value'):
                        emoji = "🌍" if message_data.role == "user" else "🤖"
                        print(f"{emoji} {message_data.role.upper()}: {content.text.value}\n")
                        break

        # Cleanup resources
        print("=" * 60)
        print("🧹 Cleaning up resources...")
        print("=" * 60)

        delete_on_exit = os.getenv("DELETE_AGENT_ON_EXIT", "true").lower() == "true"
        if delete_on_exit:
            agents_client.delete_agent(agent.id)
            print(f"✅ Deleted agent: {agent.id}")
        else:
            print(f"ℹ️  Agent {agent.id} preserved for examination in Azure AI Foundry")

        agents_client.threads.delete(thread.id)
        print(f"✅ Deleted thread: {thread.id}")
        print("=" * 60)
        print("👋 Goodbye!")
        print("=" * 60)


if __name__ == '__main__':
    main()
