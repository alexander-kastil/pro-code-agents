---
lab:
    title: 'Use a custom function in an AI agent'
    description: 'Learn how to use functions to add custom capabilities to your agents.'
---

# Use a custom function in an AI agent

In this exercise you'll explore creating an agent that can use custom functions as a tool to complete tasks. You'll build a simple technical support agent that can collect details of a technical problem and generate a support ticket.

> **Tip**: The code used in this exercise is based on the for Microsoft Foundry SDK for Python. You can develop similar solutions using the SDKs for Microsoft .NET, JavaScript, and Java. Refer to [Microsoft Foundry SDK client libraries](https://learn.microsoft.com/azure/ai-foundry/how-to/develop/sdk-overview) for details.

This exercise should take approximately **30** minutes to complete.

> **Note**: Some of the technologies used in this exercise are in preview or in active development. You may experience some unexpected behavior, warnings, or errors.

## Access the existing Foundry project

You'll use an existing Foundry project that has been pre-configured for this lab.

1. In a web browser, open the [Foundry portal](https://ai.azure.com) at `https://ai.azure.com` and sign in using your Azure credentials. Close any tips or quick start panes that are opened the first time you sign in, and if necessary use the **Foundry** logo at the top left to navigate to the home page, which looks similar to the following image (close the **Help** pane if it's open):

    ![Screenshot of Foundry portal.](./_images/ai-foundry-home.png)

   > **Important**: Make sure the **New Foundry** toggle is _Off_ for this lab.

1. In the home page, select **All resources** from the left navigation pane.
1. Locate and select the project named **pro-code-agents-student**.
1. In the navigation pane on the left, select **Overview** to see the main page for your project; which looks like this:

    ![Screenshot of a Foundry project overview page.](./_images/ai-foundry-project.png)

1. Copy the **Foundry project endpoint** values to a notepad, as you'll use them to connect to your project in a client application.

The project has several pre-deployed models available for use, including **gpt-4o**, **gpt-4o-mini**, **gpt-4.1-mini**, **gpt-5-mini**, and **text-embedding-ada-002**.

## Develop an agent that uses function tools

Now that you've accessed your project in AI Foundry, let's develop an app that implements an agent using custom function tools.

### Prepare your development environment

You have three options for your development environment:
- **GitHub Codespaces**: A cloud-based development environment
- **Local Development in Dev Containers**: Using Docker and VS Code
- **Fallback VM**: Provided by your instructor if the above options are not available

Open a terminal in your chosen environment and navigate to the lab files.

1. Change to the working directory containing the code files for this lab:

   ```
   cd /workspaces/pro-code-agents/labs/PROCESSED/lab-03/labfiles/Python
   ls -a -l
   ```

   The provided files include application code and a file for configuration settings.

### Configure the application settings

1. In the terminal, enter the following command to install the libraries you'll use:

   ```
   python -m venv labenv
   source labenv/bin/activate  # On Windows: labenv\Scripts\activate
   pip install -r requirements.txt azure-ai-projects azure-ai-agents
   ```

   > **Note:** You can ignore any warning or error messages displayed during the library installation.

1. Enter the following command to edit the configuration file that has been provided:

   ```
   code .env
   ```

   The file is opened in a code editor.

1. In the code file, replace the **your_project_endpoint** placeholder with the endpoint for your project (copied from the project **Overview** page in the Foundry portal) and ensure that the MODEL_DEPLOYMENT_NAME variable is set to **gpt-4o**.
1. After you've replaced the placeholder, save your changes and close the code editor.

### Define a custom function

1. Enter the following command to edit the code file that has been provided for your function code:

   ```
   code user_functions.py
   ```

1. Find the comment **Create a function to submit a support ticket** and add the following code, which generates a ticket number and saves a support ticket as a text file.

   ```python
   # Create a function to submit a support ticket
   def submit_support_ticket(email_address: str, description: str) -> str:
       script_dir = Path(__file__).parent  # Get the directory of the script
       ticket_number = str(uuid.uuid4()).replace('-', '')[:6]
       file_name = f"ticket-{ticket_number}.txt"
       file_path = script_dir / file_name
       text = f"Support ticket: {ticket_number}\nSubmitted by: {email_address}\nDescription:\n{description}"
       file_path.write_text(text)

       message_json = json.dumps({"message": f"Support ticket {ticket_number} submitted. The ticket file is saved as {file_name}"})
       return message_json
   ```

1. Find the comment **Define a set of callable functions** and add the following code, which statically defines a set of callable functions in this code file (in this case, there's only one - but in a real solution you may have multiple functions that your agent can call):

   ```python
   # Define a set of callable functions
   user_functions: Set[Callable[..., Any]] = {
       submit_support_ticket
   }
   ```

1. Save the file.

### Write code to implement an agent that can use your function

1. Enter the following command to begin editing the agent code.

   ```
   code agent.py
   ```

   > **Tip**: As you add code to the code file, be sure to maintain the correct indentation.

1. Review the existing code, which retrieves the application configuration settings and sets up a loop in which the user can enter prompts for the agent. The rest of the file includes comments where you'll add the necessary code to implement your technical support agent.
1. Find the comment **Add references** and add the following code to import the classes you'll need to build an Azure AI agent that uses your function code as a tool:

   ```python
   # Add references
   from azure.identity import DefaultAzureCredential
   from azure.ai.agents import AgentsClient
   from azure.ai.agents.models import FunctionTool, ToolSet, ListSortOrder, MessageRole
   from user_functions import user_functions
   ```

1. Find the comment **Connect to the Agent client** and add the following code to connect to the Azure AI project using the current Azure credentials.

   > **Tip**: Be careful to maintain the correct indentation level.

   ```python
   # Connect to the Agent client
   agent_client = AgentsClient(
      endpoint=project_endpoint,
      credential=DefaultAzureCredential
          (exclude_environment_credential=True,
           exclude_managed_identity_credential=True)
   )
   ```

1. Find the comment **Define an agent that can use the custom functions** section, and add the following code to add your function code to a toolset, and then create an agent that can use the toolset and a thread on which to run the chat session.

   ```python
   # Define an agent that can use the custom functions
   with agent_client:

       functions = FunctionTool(user_functions)
       toolset = ToolSet()
       toolset.add(functions)
       agent_client.enable_auto_function_calls(toolset)

       agent = agent_client.create_agent(
           model=model_deployment,
           name="support-agent-xxx",
           instructions="""You are a technical support agent.
                           When a user has a technical issue, you get their email address and a description of the issue.
                           Then you use those values to submit a support ticket using the function available to you.
                           If a file is saved, tell the user the file name.
                        """,
           toolset=toolset
       )

       thread = agent_client.threads.create()
       print(f"You're chatting with: {agent.name} ({agent.id})")

   ```

   > **Note**: To avoid naming conflicts with other students, use "support-agent-xxx" where `xxx` is the first three letters of your first name (e.g., "support-agent-ali" for Alice).

1. Find the comment **Send a prompt to the agent** and add the following code to add the user's prompt as a message and run the thread.

   ```python
   # Send a prompt to the agent
   message = agent_client.messages.create(
       thread_id=thread.id,
       role="user",
       content=user_prompt
   )
   run = agent_client.runs.create_and_process(thread_id=thread.id, agent_id=agent.id)
   ```

   > **Note**: Using the **create_and_process** method to run the thread enables the agent to automatically find your functions and choose to use them based on their names and parameters. As an alternative, you could use the **create_run** method, in which case you would be responsible for writing code to poll for run status to determine when a function call is required, call the function, and return the results to the agent.

1. Find the comment **Check the run status for failures** and add the following code to show any errors that occur.

   ```python
   # Check the run status for failures
   if run.status == "failed":
       print(f"Run failed: {run.last_error}")
   ```

1. Find the comment **Show the latest response from the agent** and add the following code to retrieve the messages from the completed thread and display the last one that was sent by the agent.

   ```python
   # Show the latest response from the agent
   last_msg = agent_client.messages.get_last_message_text_by_role(
      thread_id=thread.id,
      role=MessageRole.AGENT,
   )
   if last_msg:
       print(f"Last Message: {last_msg.text.value}")
   ```

1. Find the comment **Get the conversation history** and add the following code to print out the messages from the conversation thread; ordering them in chronological sequence

   ```python
   # Get the conversation history
   print("\nConversation Log:\n")
   messages = agent_client.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)
   for message in messages:
       if message.text_messages:
          last_msg = message.text_messages[-1]
          print(f"{message.role}: {last_msg.text.value}\n")
   ```

1. Find the comment **Clean up** and add the following code to delete the agent and thread when no longer needed.

   ```python
   # Clean up
   agent_client.delete_agent(agent.id)
   print("Deleted agent")
   ```

1. Review the code, using the comments to understand how it:

   - Adds your set of custom functions to a toolset
   - Creates an agent that uses the toolset.
   - Runs a thread with a prompt message from the user.
   - Checks the status of the run in case there's a failure
   - Retrieves the messages from the completed thread and displays the last one sent by the agent.
   - Displays the conversation history
   - Deletes the agent and thread when they're no longer required.

1. Save the code file when you have finished. You can also close the code editor; though you may want to keep it open in case you need to make any edits to the code you added.

### Run the app

1. In the terminal, enter the following command to run the application:

   ```
   python agent.py
   ```

   The application runs using your Azure credentials to connect to your project and create and run the agent.

1. When prompted, enter a prompt such as:

   ```
   I have a technical problem
   ```

   > **Tip**: If the app fails because the rate limit is exceeded. Wait a few seconds and try again. If there is insufficient quota available in your subscription, the model may not be able to respond.

1. View the response. The agent may ask for your email address and a description of the issue. You can use any email address (for example, `alex@contoso.com`) and any issue description (for example `my computer won't start`)

   When it has enough information, the agent should choose to use your function as required.

1. You can continue the conversation if you like. The thread is _stateful_, so it retains the conversation history - meaning that the agent has the full context for each response. Enter `quit` when you're done.
1. Review the conversation messages that were retrieved from the thread, and the tickets that were generated.
1. The tool should have saved support tickets in the app folder. You can use the `ls` command to check, and then use the `cat` command to view the file contents, like this:

   ```
   cat ticket-<ticket_num>.txt
   ```
