---
lab:
    title: 'Develop an Azure AI agent with the Microsoft Agent Framework SDK'
    description: 'Learn how to use the Microsoft Agent Framework SDK to create and use an Azure AI chat agent.'
---

# Develop an Azure AI chat agent with the Microsoft Agent Framework SDK

In this exercise, you'll use Azure AI Agent Service and Microsoft Agent Framework to create an AI agent that processes expense claims.

This exercise should take approximately **30** minutes to complete.

> **Note**: Some of the technologies used in this exercise are in preview or in active development. You may experience some unexpected behavior, warnings, or errors.

## Access the existing Foundry project

You'll use an existing Foundry project that has been pre-configured for this lab.

1. In a web browser, open the [Foundry portal](https://ai.azure.com) at `https://ai.azure.com` and sign in using your Azure credentials. Close any tips or quick start panes that are opened the first time you sign in, and if necessary use the **Foundry** logo at the top left to navigate to the home page, which looks similar to the following image (close the **Help** pane if it's open):

   ![Screenshot of Foundry portal.](../Media/ai-foundry-home.png)

   > **Important**: Make sure the **New Foundry** toggle is _Off_ for this lab.

1. In the home page, select **All resources** from the left navigation pane.
1. Locate and select the project named **pro-code-agents-student**.
1. In the navigation pane on the left, select **Models and endpoints** to verify that the **gpt-4o** model is deployed and available.
1. In the navigation pane on the left, select **Overview** to see the main page for your project; which looks like this:

   ![Screenshot of a Azure AI project details in Foundry portal.](../Media/ai-foundry-project.png)

The project has several pre-deployed models available for use, including **gpt-4o**, **gpt-4o-mini**, **gpt-4.1-mini**, **gpt-5-mini**, and **text-embedding-ada-002**.

## Create an agent client app

Now you're ready to create a client app that defines an agent and a custom function. The code files are provided in the labfiles folder.

### Prepare your development environment

You have three options for your development environment:
- **GitHub Codespaces**: A cloud-based development environment
- **Local Development in Dev Containers**: Using Docker and VS Code
- **Fallback VM**: Provided by your instructor if the above options are not available

Open a terminal in your chosen environment and navigate to the lab files.

1. Change to the working directory containing the code files for this lab:

   ```
   cd /workspaces/pro-code-agents/labs/PROCESSED/lab-07/labfiles/python
   ls -a -l
   ```

   The provided files include application code a file for configuration settings, and a file containing expenses data.

### Configure the application settings

1. In the cloud shell command-line pane, enter the following command to install the libraries you'll use:

   ```
   python -m venv labenv
   ./labenv/bin/Activate.ps1
   pip install azure-identity agent-framework
   ```

1. Enter the following command to edit the configuration file that has been provided:

   ```
   code .env
   ```

   The file is opened in a code editor.

1. In the code file, replace the **your_project_endpoint** placeholder with the endpoint for your project (copied from the project **Overview** page in the Foundry portal), and the **your_model_deployment** placeholder with the name you assigned to your gpt-4o model deployment.
1. After you've replaced the placeholders, save your changes and then close the code editor.

### Write code for an agent app

> **Tip**: As you add code, be sure to maintain the correct indentation. Use the existing comments as a guide, entering the new code at the same level of indentation.

1. Enter the following command to edit the agent code file that has been provided:

   ```
   code agent-framework.py
   ```

1. Review the code in the file. It contains:

   - Some **import** statements to add references to commonly used namespaces
   - A _main_ function that loads a file containing expenses data, asks the user for instructions, and and then calls...
   - A **process_expenses_data** function in which the code to create and use your agent must be added

1. At the top of the file, after the existing **import** statement, find the comment **Add references**, and add the following code to reference the namespaces in the libraries you'll need to implement your agent:

   ```python
   # Add references
   from agent_framework import AgentThread, ChatAgent
   from agent_framework.azure import AzureAIAgentClient
   from azure.identity.aio import AzureCliCredential
   from pydantic import Field
   from typing import Annotated
   ```

1. Near the bottom of the file, find the comment **Create a tool function for the email functionality**, and add the following code to define a function that your agent will use to send email (tools are a way to add custom functionality to agents)

   ```python
   # Create a tool function for the email functionality
   def send_email(
   to: Annotated[str, Field(description="Who to send the email to")],
   subject: Annotated[str, Field(description="The subject of the email.")],
   body: Annotated[str, Field(description="The text body of the email.")]):
       print("\nTo:", to)
       print("Subject:", subject)
       print(body, "\n")
   ```

   > **Note**: The function _simulates_ sending an email by printing it to the console. In a real application, you'd use an SMTP service or similar to actually send the email!

1. Back up above the **send_email** code, in the **process_expenses_data** function, find the comment **Create a chat agent**, and add the following code to create a **ChatAgent** object with the tools and instructions.

   (Be sure to maintain the indentation level)

   ```python
   # Create a chat agent
   async with (
      AzureCliCredential() as credential,
      ChatAgent(
          chat_client=AzureAIAgentClient(async_credential=credential),
          name="expenses_agent",
          instructions="""You are an AI assistant for expense claim submission.
                          When a user submits expenses data and requests an expense claim, use the plug-in function to send an email to expenses@contoso.com with the subject 'Expense Claim`and a body that contains itemized expenses with a total.
                          Then confirm to the user that you've done so.""",
          tools=send_email,
      ) as agent,
   ):
   ```

   Note that the **AzureCliCredential** object will allow your code to authenticate to your Azure account. The **AzureAIAgentClient** object will automatically include the Foundry project settings from the .env configuration.

1. Find the comment **Use the agent to process the expenses data**, and add the following code to create a thread for your agent to run on, and then invoke it with a chat message.

   (Be sure to maintain the indentation level):

   ```python
   # Use the agent to process the expenses data
   try:
      # Add the input prompt to a list of messages to be submitted
      prompt_messages = [f"{prompt}: {expenses_data}"]
      # Invoke the agent for the specified thread with the messages
      response = await agent.run(prompt_messages)
      # Display the response
      print(f"\n# Agent:\n{response}")
   except Exception as e:
      # Something went wrong
      print (e)
   ```

1. Review that the completed code for your agent, using the comments to help you understand what each block of code does, and then save your code changes.
1. Keep the code editor open in case you need to correct any typo's in the code.

### Run the app

1. In the terminal, enter the following command to run the application:

   ```
   python agent-framework.py
   ```

   The application runs using your Azure credentials to connect to your project and create and run the agent.

1. When asked what to do with the expenses data, enter the following prompt:

   ```
   Submit an expense claim
   ```

1. When the application has finished, review the output. The agent should have composed an email for an expenses claim based on the data that was provided.

   > **Tip**: If the app fails because the rate limit is exceeded. Wait a few seconds and try again. If there is insufficient quota available in your subscription, the model may not be able to respond.

## Summary

In this exercise, you used the Microsoft Agent Framework SDK to create an agent with a custom tool.
