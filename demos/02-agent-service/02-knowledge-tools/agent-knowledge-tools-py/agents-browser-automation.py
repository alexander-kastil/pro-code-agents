import os
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.ai.agents.models import (
    MessageRole,
    RunStepToolCallDetails,
    BrowserAutomationTool,
    RunStepBrowserAutomationToolCall,
)
from azure.identity import DefaultAzureCredential

def main():
    # Clear the console to keep the output focused on the agent interaction
    os.system('cls' if os.name == 'nt' else 'clear')

    # Load environment variables from .env file
    load_dotenv()
    endpoint = os.getenv("PROJECT_ENDPOINT")
    model = os.getenv("MODEL_DEPLOYMENT")
    connection_id = os.getenv("AZURE_PLAYWRIGHT_CONNECTION_ID")

    print(f"Using endpoint: {endpoint}")
    print(f"Using model: {model}")
    print(f"Using connection_id: {connection_id}")

    project_client = AIProjectClient(
        endpoint=endpoint,
        credential=DefaultAzureCredential(),
    )

    # [START create_agent_with_browser_automation]
    # Initialize Browser Automation tool and add the connection id
    browser_automation = BrowserAutomationTool(connection_id=connection_id)

    with project_client:

        agents_client = project_client.agents

        # Create a new Agent that has the Browser Automation tool attached.
        # Note: To add Browser Automation tool to an existing Agent with an `agent_id`, do the following:
        # agent = agents_client.update_agent(agent_id, tools=browser_automation.definitions)
        agent = agents_client.create_agent(
            model=model,
            name="my-agent",
            instructions="""
            You are an Agent helping with browser automation tasks. 
            You can answer questions, provide information, and assist with various tasks 
            related to web browsing using the Browser Automation tool available to you.
            """,
            description="Demonstrates Browser Automation using Playwright to navigate websites, interact with elements, and extract data from web pages.",
            tools=browser_automation.definitions,
        )

        # [END create_agent_with_browser_automation]

        print(f"Created agent, agent ID: {agent.id}")

        # Create thread for communication
        thread = agents_client.threads.create()
        print(f"Created thread, thread ID: {thread.id}")

        # Create message to thread
        message = agents_client.messages.create(
            thread_id=thread.id,
            role=MessageRole.USER,
            content="""
            Your goal is to report the percent of Microsoft year-to-date stock price change.
            To do that, go to the website finance.yahoo.com.
            At the top of the page, you will find a search bar.
            Enter the value 'MSFT', to get information about the Microsoft stock price.
            At the top of the resulting page you will see a default chart of Microsoft stock price.
            Click on 'YTD' at the top of that chart, and report the percent value that shows up just below it.
            """,
        )
        print(f"Created message, message ID: {message.id}")

        # Create and process agent run in thread with tools
        print(f"Waiting for Agent run to complete. Please wait...")
        run = agents_client.runs.create_and_process(thread_id=thread.id, agent_id=agent.id)
        print(f"Run finished with status: {run.status}")

        if run.status == "failed":
            print(f"Run failed: {run.last_error}")

        # Fetch run steps to get the details of the agent run
        run_steps = agents_client.run_steps.list(thread_id=thread.id, run_id=run.id)
        for step in run_steps:
            print(f"Step {step.id} status: {step.status}")

            if isinstance(step.step_details, RunStepToolCallDetails):
                print("  Tool calls:")
                tool_calls = step.step_details.tool_calls

                for call in tool_calls:
                    print(f"    Tool call ID: {call.id}")
                    print(f"    Tool call type: {call.type}")

                    if isinstance(call, RunStepBrowserAutomationToolCall):
                        print(f"    Browser automation input: {call.browser_automation.input}")
                        print(f"    Browser automation output: {call.browser_automation.output}")

                        print("    Steps:")
                        for tool_step in call.browser_automation.steps:
                            print(f"      Last step result: {tool_step.last_step_result}")
                            print(f"      Current state: {tool_step.current_state}")
                            print(f"      Next step: {tool_step.next_step}")
                            print()  # add an extra newline between tool steps

                    print()  # add an extra newline between tool calls

            print()  # add an extra newline between run steps

        # Optional: Delete the agent once the run is finished.
        # Controlled by DELETE_AGENT_ON_EXIT environment variable
        delete_on_exit = os.getenv("DELETE_AGENT_ON_EXIT", "true").lower() == "true"
        if delete_on_exit:
            agents_client.delete_agent(agent.id)
            print("Deleted agent")
        else:
            print(f"Agent {agent.id} preserved for examination in Azure AI Foundry")

        # Print the Agent's response message with optional citation
        response_message = agents_client.messages.get_last_message_by_role(thread_id=thread.id, role=MessageRole.AGENT)
        if response_message:
            for text_message in response_message.text_messages:
                print(f"Agent response: {text_message.text.value}")
            for annotation in response_message.url_citation_annotations:
                print(f"URL Citation: [{annotation.url_citation.title}]({annotation.url_citation.url})")


if __name__ == '__main__':
    main()
