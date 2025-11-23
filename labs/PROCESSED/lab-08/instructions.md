---
lab:
    title: 'Develop a multi-agent solution with Microsoft Agent Framework'
    description: 'Learn to configure multiple agents to collaborate using the Microsoft Agent Framework SDK'
---

# Develop a multi-agent solution

In this exercise, you'll practice using the sequential orchestration pattern in the Microsoft Agent Framework SDK. You'll create a simple pipeline of three agents that work together to process customer feedback and suggest next steps. You'll create the following agents:

- The Summarizer agent will condense raw feedback into a short, neutral sentence.
- The Classifier agent will categorize the feedback as Positive, Negative, or a Feature request.
- Finally, the Recommended Action agent will recommend an appropriate follow-up step.

You'll learn how to use the Microsoft Agent Framework SDK to break down a problem, route it through the right agents, and produce actionable results. Let's get started!

This exercise should take approximately **30** minutes to complete.

> **Note**: Some of the technologies used in this exercise are in preview or in active development. You may experience some unexpected behavior, warnings, or errors.

## Access the existing Foundry project

You'll use an existing Foundry project that has been pre-configured for this lab.

1. In a web browser, open the [Foundry portal](https://ai.azure.com) at `https://ai.azure.com` and sign in using your Azure credentials. Close any tips or quick start panes that are opened the first time you sign in, and if necessary use the **Foundry** logo at the top left to navigate to the home page, which looks similar to the following image (close the **Help** pane if it's open):

    ![Screenshot of Foundry portal.](./_images/ai-foundry-home.png)

   > **Important**: Make sure the **New Foundry** toggle is _Off_ for this lab.

1. In the home page, select **All resources** from the left navigation pane.
1. Locate and select the project named **pro-code-agents-student**.
1. In the navigation pane on the left, select **Models and endpoints** to verify that the **gpt-4o** model is deployed and available.
1. In the navigation pane on the left, select **Overview** to see the main page for your project; which looks like this:

    ![Screenshot of a Azure AI project details in Foundry portal.](./_images/ai-foundry-project.png)

The project has several pre-deployed models available for use, including **gpt-4o**, **gpt-4o-mini**, **gpt-4.1-mini**, **gpt-5-mini**, and **text-embedding-ada-002**.

## Create an AI Agent client app

Now you're ready to create a client app that defines an agent and a custom function. The code files are provided in the labfiles folder.

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

   The provided files include application code and a file for configuration settings.

### Configure the application settings

1. In the terminal, enter the following command to install the libraries you'll use:

   ```
   python -m venv labenv
   source labenv/bin/activate  # On Windows: labenv\Scripts\activate
   pip install azure-identity agent-framework
   ```

1. Enter the following command to edit the configuration file that is provided:

   ```
   code .env
   ```

   The file is opened in a code editor.

1. In the code file, replace the **your_openai_endpoint** placeholder with the endpoint for your project (copied from the project **Overview** page in the Foundry portal). Replace the **your_model_deployment** placeholder with **gpt-4o**.

1. After you've replaced the placeholders, save your changes and then close the code editor.

### Create AI agents

Now you're ready to create the agents for your multi-agent solution! Let's get started!

1. Enter the following command to edit the **agents.py** file:

   ```
   code agents.py
   ```

1. At the top of the file under the comment **Add references**, and add the following code to reference the namespaces in the libraries you'll need to implement your agent:

   ```python
   # Add references
   import asyncio
   from typing import cast
   from agent_framework import ChatMessage, Role, SequentialBuilder, WorkflowOutputEvent
   from agent_framework.azure import AzureAIAgentClient
   from azure.identity import AzureCliCredential
   ```

1. In the **main** function, take a moment to review the agent instructions. These instructions define the behavior of each agent in the orchestration.

1. Add the following code under the comment **Create the chat client**:

   ```python
   # Create the chat client
   credential = AzureCliCredential()
   async with (
      AzureAIAgentClient(async_credential=credential) as chat_client,
   ):
   ```

   Note that the **AzureCliCredential** object will allow your code to authenticate to your Azure account. The **AzureAIAgentClient** object will automatically include the Foundry project settings from the .env configuration.

1. Add the following code under the comment **Create agents**:

   (Be sure to maintain the indentation level)

   ```python
   # Create agents
   summarizer = chat_client.create_agent(
      instructions=summarizer_instructions,
      name="summarizer",
   )

   classifier = chat_client.create_agent(
      instructions=classifier_instructions,
      name="classifier",
   )

   action = chat_client.create_agent(
      instructions=action_instructions,
      name="action",
   )
   ```

## Create a sequential orchestration

1. In the **main** function, find the comment **Initialize the current feedback** and add the following code:

   (Be sure to maintain the indentation level)

   ```python
   # Initialize the current feedback
   feedback="""
   I use the dashboard every day to monitor metrics, and it works well overall.
   But when I'm working late at night, the bright screen is really harsh on my eyes.
   If you added a dark mode option, it would make the experience much more comfortable.
   """
   ```

1. Under the comment **Build a sequential orchestration**, add the following code to define a sequential orchestration with the agents you defined:

   ```python
   # Build sequential orchestration
   workflow = SequentialBuilder().participants([summarizer, classifier, action]).build()
   ```

   The agents will process the feedback in the order they are added to the orchestration.

1. Add the following code under the comment **Run and collect outputs**:

   ```python
   # Run and collect outputs
   outputs: list[list[ChatMessage]] = []
   async for event in workflow.run_stream(f"Customer feedback: {feedback}"):
      if isinstance(event, WorkflowOutputEvent):
          outputs.append(cast(list[ChatMessage], event.data))
   ```

   This code runs the orchestration and collects the output from each of the participating agents.

1. Add the following code under the comment **Display outputs**:

   ```python
   # Display outputs
   if outputs:
      for i, msg in enumerate(outputs[-1], start=1):
          name = msg.author_name or ("assistant" if msg.role == Role.ASSISTANT else "user")
          print(f"{'-' * 60}\n{i:02d} [{name}]\n{msg.text}")
   ```

   This code formats and displays the messages from the workflow outputs you collected from the orchestration.

1. Save your changes to the code file. You can keep it open in case you need to edit the code to fix any errors.

### Run the app

Now you're ready to run your code and watch your AI agents collaborate.

1. In the terminal, enter the following command to run the application:

   ```
   python agents.py
   ```

   You should see some output similar to the following:

   ```output
   ------------------------------------------------------------
   01 [user]
   Customer feedback:
       I use the dashboard every day to monitor metrics, and it works well overall.
       But when I'm working late at night, the bright screen is really harsh on my eyes.
       If you added a dark mode option, it would make the experience much more comfortable.

   ------------------------------------------------------------
   02 [summarizer]
   User requests a dark mode for better nighttime usability.
   ------------------------------------------------------------
   03 [classifier]
   Feature request
   ------------------------------------------------------------
   04 [action]
   Log as enhancement request for product backlog.
   ```

1. Optionally, you can try running the code using different feedback inputs, such as:

   ```output
   I use the dashboard every day to monitor metrics, and it works well overall. But when I'm working late at night, the bright screen is really harsh on my eyes. If you added a dark mode option, it would make the experience much more comfortable.
   ```

   ```output
   I reached out to your customer support yesterday because I couldn't access my account. The representative responded almost immediately, was polite and professional, and fixed the issue within minutes. Honestly, it was one of the best support experiences I've ever had.
   ```

## Summary

In this exercise, you practiced sequential orchestration with the Microsoft Agent Framework SDK, combining multiple agents into a single, streamlined workflow. Great work!
