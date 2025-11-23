---
lab:
    title: 'Develop an AI agent'
    description: 'Use the Azure AI Agent Service to develop an agent that uses built-in tools.'
---

# Develop an AI agent

In this exercise, you'll use Azure AI Agent Service to create a simple agent that analyzes data and creates charts. The agent can use the built-in _Code Interpreter_ tool to dynamically generate any code required to analyze data.

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

## Create an agent client app

Now you're ready to create a client app that uses an agent. The code files are provided in the labfiles folder.

### Prepare your development environment

You have three options for your development environment:
- **GitHub Codespaces**: A cloud-based development environment
- **Local Development in Dev Containers**: Using Docker and VS Code
- **Fallback VM**: Provided by your instructor if the above options are not available

Open a terminal in your chosen environment and navigate to the lab files.

1. Change to the working directory containing the code files for this lab:

   ```
   cd labfiles/Python
   ls -a -l
   ```

   The provided files include application code, configuration settings, and data.

### Configure the application settings

1. In the terminal, enter the following command to install the libraries you'll use:

   ```
   python -m venv labenv
   source labenv/bin/activate  # On Windows: labenv\Scripts\activate
   pip install -r requirements.txt azure-ai-projects azure-ai-agents
   ```

1. Enter the following command to edit the configuration file that has been provided:

   ```
   code .env
   ```

   The file is opened in a code editor.

1. In the code file, replace the **your_project_endpoint** placeholder with the endpoint for your project (copied from the project **Overview** page in the Foundry portal) and ensure that the MODEL_DEPLOYMENT_NAME variable is set to **gpt-4o**.
1. After you've replaced the placeholder, save your changes and close the code editor.

### Write code for an agent app

> **Tip**: As you add code, be sure to maintain the correct indentation. Use the comment indentation levels as a guide.

1. Enter the following command to edit the code file that has been provided:

   ```
   code agent.py
   ```

1. Review the existing code, which retrieves the application configuration settings and loads data from _data.txt_ to be analyzed. The rest of the file includes comments where you'll add the necessary code to implement your data analysis agent.
1. Find the comment **Add references** and add the following code to import the classes you'll need to build an Azure AI agent that uses the built-in code interpreter tool:

   ```python
   # Add references
   from azure.identity import DefaultAzureCredential
   from azure.ai.agents import AgentsClient
   from azure.ai.agents.models import FilePurpose, CodeInterpreterTool, ListSortOrder, MessageRole
   ```

1. Find the comment **Connect to the Agent client** and add the following code to connect to the Azure AI project.

   > **Tip**: Be careful to maintain the correct indentation level.

   ```python
   # Connect to the Agent client
   agent_client = AgentsClient(
      endpoint=project_endpoint,
      credential=DefaultAzureCredential
          (exclude_environment_credential=True,
           exclude_managed_identity_credential=True)
   )
   with agent_client:
   ```

   The code connects to the Foundry project using the current Azure credentials. The final _with agent_client_ statement starts a code block that defines the scope of the client, ensuring it's cleaned up when the code within the block is finished.

1. Find the comment **Upload the data file and create a CodeInterpreterTool**, within the _with agent_client_ block, and add the following code to upload the data file to the project and create a CodeInterpreterTool that can access the data in it:

   ```python
   # Upload the data file and create a CodeInterpreterTool
   file = agent_client.files.upload_and_poll(
       file_path=file_path, purpose=FilePurpose.AGENTS
   )
   print(f"Uploaded {file.filename}")

   code_interpreter = CodeInterpreterTool(file_ids=[file.id])
   ```

1. Find the comment **Define an agent that uses the CodeInterpreterTool** and add the following code to define an AI agent that analyzes data and can use the code interpreter tool you defined previously:

   ```python
   # Define an agent that uses the CodeInterpreterTool
   agent = agent_client.create_agent(
       model=model_deployment,
       name="data-agent-xxx",
       instructions="You are an AI agent that analyzes the data in the file that has been uploaded. Use Python to calculate statistical metrics as necessary.",
       tools=code_interpreter.definitions,
       tool_resources=code_interpreter.resources,
   )
   print(f"Using agent: {agent.name}")
   ```

   > **Note**: To avoid naming conflicts with other students, use "data-agent-xxx" where `xxx` is the first three letters of your first name (e.g., "data-agent-ali" for Alice).

1. Find the comment **Create a thread for the conversation** and add the following code to start a thread on which the chat session with the agent will run:

   ```python
   # Create a thread for the conversation
   thread = agent_client.threads.create()
   ```

1. Note that the next section of code sets up a loop for a user to enter a prompt, ending when the user enters "quit".

1. Find the comment **Send a prompt to the agent** and add the following code to add a user message to the prompt (along with the data from the file that was loaded previously), and then run thread with the agent.

   ```python
   # Send a prompt to the agent
   message = agent_client.messages.create(
       thread_id=thread.id,
       role="user",
       content=user_prompt,
   )

   run = agent_client.runs.create_and_process(thread_id=thread.id, agent_id=agent.id)
   ```

1. Find the comment **Check the run status for failures** and add the following code to check for any errors.

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

1. Find the comment **Get the conversation history**, which is after the loop ends, and add the following code to print out the messages from the conversation thread; reversing the order to show them in chronological sequence

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
   ```

1. Review the code, using the comments to understand how it:

   - Connects to the AI Foundry project.
   - Uploads the data file and creates a code interpreter tool that can access it.
   - Creates a new agent that uses the code interpreter tool and has explicit instructions to use Python as necessary for statistical analysis.
   - Runs a thread with a prompt message from the user along with the data to be analyzed.
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

1. When prompted, view the data that the app has loaded from the _data.txt_ text file. Then enter a prompt such as:

   ```
   What's the category with the highest cost?
   ```

   > **Tip**: If the app fails because the rate limit is exceeded. Wait a few seconds and try again. If there is insufficient quota available in your subscription, the model may not be able to respond.

1. View the response. Then enter another prompt, this time requesting a visualization:

   ```
   Create a text-based bar chart showing cost by category
   ```

1. View the response. Then enter another prompt, this time requesting a statistical metric:

   ```
   What's the standard deviation of cost?
   ```

   View the response.

1. You can continue the conversation if you like. The thread is _stateful_, so it retains the conversation history - meaning that the agent has the full context for each response. Enter `quit` when you're done.
1. Review the conversation messages that were retrieved from the thread - which may include messages the agent generated to explain its steps when using the code interpreter tool.

## Summary

In this exercise, you used the Azure AI Agent Service SDK to create a client application that uses an AI agent. The agent can use the built-in Code Interpreter tool to run dynamic Python code to perform statistical analyses.
