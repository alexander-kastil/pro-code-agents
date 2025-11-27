import os
from datetime import datetime
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition

load_dotenv('.env')

endpoint = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
model = os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME", "gpt-4o")
delete_resources = os.getenv("DELETE", "true").lower() == "true"


# ============================================================================
# MIDDLEWARE IMPLEMENTATIONS (Foundry-compatible)
# ============================================================================

class TimingMiddleware:
    """Tracks execution time for requests."""
    
    def __init__(self):
        self.start_time = None
    
    def before_request(self):
        self.start_time = datetime.now()
        print(f"\n[TIMING] Started at {self.start_time.strftime('%H:%M:%S')}")
    
    def after_request(self):
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        print(f"[TIMING] Completed in {duration:.2f} seconds")


class SecurityMiddleware:
    """Blocks requests containing sensitive keywords."""
    
    BLOCKED_KEYWORDS = ["password", "secret", "hack", "exploit", "bypass"]
    
    def check_request(self, user_input: str) -> bool:
        """Returns True if request is allowed, False if blocked."""
        text = user_input.lower()
        for keyword in self.BLOCKED_KEYWORDS:
            if keyword in text:
                print(f"\n[SECURITY] Request BLOCKED! Detected: '{keyword}'")
                print(f"[SECURITY] This request contains sensitive content and cannot be processed.")
                return False
        return True


class TokenCounterMiddleware:
    """Estimates and logs token usage for AI calls."""
    
    def estimate_tokens(self, messages: list, response_text: str):
        """Estimate token usage based on character count."""
        total_chars = sum(len(str(msg.get('content', ''))) for msg in messages)
        estimated_input_tokens = total_chars // 4
        
        print(f"\n[AI CALL] Sending request to model")
        print(f"[AI CALL] Messages: {len(messages)}")
        print(f"[AI CALL] Estimated input tokens: ~{estimated_input_tokens}")
        
        if response_text:
            estimated_output_tokens = len(response_text) // 4
            total_tokens = estimated_input_tokens + estimated_output_tokens
            print(f"[AI CALL] Estimated output tokens: ~{estimated_output_tokens}")
            print(f"[AI CALL] Total estimated tokens: ~{total_tokens}")


# ============================================================================
# DEMO TOOLS/FUNCTIONS
# ============================================================================

def get_weather(city: str) -> str:
    """Get current weather for a city."""
    weather_data = {
        "seattle": "Cloudy, 15°C, Light drizzle",
        "london": "Rainy, 12°C, Heavy rain",
        "tokyo": "Sunny, 22°C, Clear skies",
        "mumbai": "Partly cloudy, 28°C, Humid",
        "paris": "Partly cloudy, 18°C, Mild",
        "new york": "Snowy, -2°C, Light snow",
    }
    result = weather_data.get(city.lower(), f"Weather data not available for {city}")
    print(f"\n[FUNCTION] Calling tool: get_weather")
    print(f"[FUNCTION] Arguments: city='{city}'")
    print(f"[FUNCTION] Result: {result}")
    return result


def calculate(expression: str) -> str:
    """Calculate a mathematical expression safely."""
    print(f"\n[FUNCTION] Calling tool: calculate")
    print(f"[FUNCTION] Arguments: expression='{expression}'")
    try:
        allowed_names = {}
        result = eval(expression, {"__builtins__": {}}, allowed_names)
        result_str = f"Result: {result}"
        print(f"[FUNCTION] Result: {result_str}")
        return result_str
    except Exception as e:
        error_str = f"Calculation error: {str(e)}"
        print(f"[FUNCTION] Result: {error_str}")
        return error_str


def get_time() -> str:
    """Get the current time."""
    print(f"\n[FUNCTION] Calling tool: get_time")
    result = f"Current time: {datetime.now().strftime('%I:%M:%S %p')}"
    print(f"[FUNCTION] Result: {result}")
    return result


def search_database(query: str) -> str:
    """Simulate searching a database."""
    print(f"\n[FUNCTION] Calling tool: search_database")
    print(f"[FUNCTION] Arguments: query='{query}'")
    results = {
        "users": "Found 150 users matching criteria",
        "products": "Found 45 products in inventory",
        "orders": "Found 230 orders in last 30 days",
    }
    result = results.get(query.lower(), f"No results found for: {query}")
    print(f"[FUNCTION] Result: {result}")
    return result


def process_tool_calls(user_input: str) -> str:
    """Process any tool calls mentioned in user input."""
    extra_context = []
    input_lower = user_input.lower()
    
    # Check for weather requests
    for city in ["seattle", "london", "tokyo", "mumbai", "paris", "new york"]:
        if city in input_lower:
            extra_context.append(f"Weather info: {get_weather(city)}")
    
    # Check for time requests
    if "time" in input_lower and "what" in input_lower:
        extra_context.append(get_time())
    
    # Check for calculation requests
    if "calculate" in input_lower:
        # Try to extract expression (simple approach)
        import re
        match = re.search(r'calculate\s+([0-9\s\+\-\*\/\(\)\.]+)', input_lower)
        if match:
            expr = match.group(1).strip()
            extra_context.append(calculate(expr))
    
    # Check for database search
    for term in ["users", "products", "orders"]:
        if f"search for {term}" in input_lower or f"search {term}" in input_lower:
            extra_context.append(search_database(term))
    
    return "\n".join(extra_context) if extra_context else ""


# ============================================================================
# MAIN INTERACTIVE DEMO
# ============================================================================

def main():
    print("\n" + "="*75)
    print("COMPLETE MIDDLEWARE DEMO - All Types Working Together")
    print("="*75)
    print("""
This demo shows middleware patterns working simultaneously:

1.  TIMING MIDDLEWARE      → Tracks how long each request takes
2.  SECURITY MIDDLEWARE    → Blocks sensitive content
3.  FUNCTION LOGGER        → Logs all tool calls
4.  TOKEN COUNTER          → Estimates tokens sent to AI

Watch how they all work together in a real conversation!
""")
    print("="*75)
    print("\nCreating agent with middleware patterns...\n")
    
    # Initialize middleware
    timing = TimingMiddleware()
    security = SecurityMiddleware()
    token_counter = TokenCounterMiddleware()
    
    # Initialize project client and OpenAI responses client
    project_client = AIProjectClient(endpoint=endpoint, credential=DefaultAzureCredential())
    openai_client = project_client.get_openai_client()
    
    with project_client:
        # Create agent
        agent = project_client.agents.create_version(
            agent_name="middleware-demo-agent",
            definition=PromptAgentDefinition(
                model=model,
                instructions="""You are a helpful assistant with access to various tools.
When the user asks about weather, time, calculations, or database searches, 
include the provided tool results in your response naturally.
Be friendly, concise, and helpful in your responses."""
            )
        )
        
        print(f"Agent created: {agent.name} (version {agent.version})")
        print("Middleware layers initialized.")
        
        print("\n" + "="*75)
        print("SUGGESTED TEST PROMPTS:")
        print("="*75)
        print("""
To see all middleware in action, try these prompts:

PROMPT 1: "tell me a joke"
   → Triggers: Timing + Token Counter
   → Simple request, no functions

PROMPT 2: "what's the weather in Tokyo?"
   → Triggers: Timing + Function Logger + Token Counter
   → Calls the get_weather function

PROMPT 3: "what time is it and calculate 15 * 8"
   → Triggers: Timing + Function Logger (2 calls) + Token Counter
   → Multiple function calls

PROMPT 4: "what is my password?"
   → Triggers: Security (BLOCKS) + Timing
   → Security middleware blocks this request!

PROMPT 5: "search for users and get weather in Paris"
   → Triggers: ALL middleware
   → Multiple functions, shows complete flow

Type 'quit' to exit
""")
        print("="*75 + "\n")
        
        # Conversation history for multi-turn support
        conversation_history = []
        
        while True:
            try:
                user_input = input("You: ").strip()
                if not user_input:
                    continue
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("\nDemo ended. Thanks for testing all the middleware.")
                    break
                
                print("\n" + "-"*75)
                print("PROCESSING YOUR REQUEST...")
                print("-"*75)
                
                # MIDDLEWARE 1: Timing - Start
                timing.before_request()
                
                # MIDDLEWARE 2: Security - Check
                if not security.check_request(user_input):
                    timing.after_request()
                    print("-"*75)
                    print("Request blocked by security middleware.\n")
                    continue
                
                # Process any tool calls in the user input
                tool_results = process_tool_calls(user_input)
                
                # Build the message with tool results if any
                message_content = user_input
                if tool_results:
                    message_content = f"{user_input}\n\n[Tool Results]:\n{tool_results}"
                
                # Add user message to history
                conversation_history.append({"role": "user", "content": message_content})
                
                # MIDDLEWARE 4: Token Counter - Before
                token_counter.estimate_tokens(conversation_history, "")
                
                # Create response using Foundry Responses API
                response = openai_client.responses.create(
                    input=conversation_history,
                    extra_body={"agent": {"type": "agent_reference", "name": agent.name, "version": agent.version}}
                )
                
                # Process response
                assistant_text = ""
                if response.status == "completed":
                    for item in response.output:
                        if item.type == "message" and item.content and item.content[0].type == "output_text":
                            assistant_text = item.content[0].text
                
                # MIDDLEWARE 4: Token Counter - After (with response)
                if assistant_text:
                    token_counter.estimate_tokens(conversation_history, assistant_text)
                
                print(f"\nAgent: {assistant_text}")
                
                # Add assistant response to history
                if assistant_text:
                    conversation_history.append({"role": "assistant", "content": assistant_text})
                
                # MIDDLEWARE 1: Timing - End
                timing.after_request()
                
                print("-"*75)
                print("Request completed.\n")
                
            except (KeyboardInterrupt, EOFError):
                print("\n\nSee you again soon.")
                break
            except Exception as e:
                print(f"\nError: {e}\n")
        
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
