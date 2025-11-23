---
lab:
    title: 'Develop a multi-agent solution with Microsoft Foundry'
    description: 'Learn to configure multiple agents to collaborate using Microsoft Foundry Agent Service'
---

# Develop a multi-agent solution

In this exercise, you'll create a project that orchestrates multiple AI agents using Microsoft Foundry Agent Service. You'll design an AI solution that assists with ticket triage. The connected agents will assess the ticket's priority, suggest a team assignment, and determine the level of effort required to complete the ticket. Let's get started!

> **Tip**: The code used in this exercise is based on the for Foundry SDK for Python. You can develop similar solutions using the SDKs for Microsoft .NET, JavaScript, and Java. Refer to [Foundry SDK client libraries](https://learn.microsoft.com/azure/ai-foundry/how-to/develop/sdk-overview) for details.

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

   ![Screenshot of a Foundry project overview page.](../Media/ai-foundry-project.png)

1. Copy the **Foundry project endpoint** values to a notepad, as you'll use them to connect to your project in a client application.

The project has several pre-deployed models available for use, including **gpt-4o**, **gpt-4o-mini**, **gpt-4.1-mini**, **gpt-5-mini**, and **text-embedding-ada-002**.

## Create an AI Agent client app

Now you're ready to create a client app that defines the agents and instructions. The code files are provided in the labfiles folder.

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
   pip install -r requirements.txt azure-ai-projects azure-ai-agents
   ```

1. Enter the following command to edit the configuration file that is provided:

   ```
   code .env
   ```

   The file is opened in a code editor.

1. In the code file, replace the **your_project_endpoint** placeholder with the endpoint for your project (copied from the project **Overview** page in the Foundry portal), and the **your_model_deployment** placeholder with **gpt-4o**.

1. After you've replaced the placeholders, save your changes and close the code editor.

### Create AI agents

Now you're ready to create the agents for your multi-agent solution! Let's get started!

1. Enter the following command to edit the **agent_triage.py** file:

   ```
   code agent_triage.py
   ```

1. Review the code in the file, noting that it contains strings for each agent name and instructions.

1. Find the comment **Add references** and add the following code to import the classes you'll need:

   ```python
   # Add references
   from azure.ai.agents import AgentsClient
   from azure.ai.agents.models import ConnectedAgentTool, MessageRole, ListSortOrder, ToolSet, FunctionTool
   from azure.identity import DefaultAzureCredential
   ```

1. Note that code to load the project endpoint and model name from your environment variables has been provided.

1. Find the comment **Connect to the agents client**, and add the following code to create an AgentsClient connected to your project:

   ```python
   # Connect to the agents client
   agents_client = AgentsClient(
       endpoint=project_endpoint,
       credential=DefaultAzureCredential(
           exclude_environment_credential=True,
           exclude_managed_identity_credential=True
       ),
   )
   ```

   Now you'll add code that uses the AgentsClient to create multiple agents, each with a specific role to play in processing a support ticket.

   > **Tip**: When adding subsequent code, be sure to maintain the right level of indentation under the `using agents_client:` statement.

1. Find the comment **Create an agent to prioritize support tickets**, and enter the following code (being careful to retain the right level of indentation):

   ```python
   # Create an agent to prioritize support tickets
   priority_agent_name = "priority_agent-xxx"
   priority_agent_instructions = """
   Assess how urgent a ticket is based on its description.

   Respond with one of the following levels:
   - High: User-facing or blocking issues
   - Medium: Time-sensitive but not breaking anything
   - Low: Cosmetic or non-urgent tasks

   Only output the urgency level and a very brief explanation.
   """

   priority_agent = agents_client.create_agent(
       model=model_deployment,
       name=priority_agent_name,
       instructions=priority_agent_instructions
   )
   ```

   > **Note**: To avoid naming conflicts with other students, use "priority_agent-xxx" where `xxx` is the first three letters of your first name (e.g., "priority_agent-ali" for Alice).

1. Find the comment **Create an agent to assign tickets to the appropriate team**, and enter the following code:

   ```python
   # Create an agent to assign tickets to the appropriate team
   team_agent_name = "team_agent-xxx"
   team_agent_instructions = """
   Decide which team should own each ticket.

   Choose from the following teams:
   - Frontend
   - Backend
   - Infrastructure
   - Marketing

   Base your answer on the content of the ticket. Respond with the team name and a very brief explanation.
   """

   team_agent = agents_client.create_agent(
       model=model_deployment,
       name=team_agent_name,
       instructions=team_agent_instructions
   )
   ```

   > **Note**: Use the same suffix (first three letters of your first name) for this agent name.

1. Find the comment **Create an agent to estimate effort for a support ticket**, and enter the following code:

   ```python
   # Create an agent to estimate effort for a support ticket
   effort_agent_name = "effort_agent-xxx"
   effort_agent_instructions = """
   Estimate how much work each ticket will require.

   Use the following scale:
   - Small: Can be completed in a day
   - Medium: 2-3 days of work
   - Large: Multi-day or cross-team effort

   Base your estimate on the complexity implied by the ticket. Respond with the effort level and a brief justification.
   """

   effort_agent = agents_client.create_agent(
       model=model_deployment,
       name=effort_agent_name,
       instructions=effort_agent_instructions
   )
   ```

   > **Note**: Use the same suffix (first three letters of your first name) for this agent name.

   So far, you've created three agents; each of which has a specific role in triaging a support ticket. Now let's create ConnectedAgentTool objects for each of these agents so they can be used by other agents.

1. Find the comment **Create connected agent tools for the support agents**, and enter the following code:

   ```python
   # Create connected agent tools for the support agents
   priority_agent_tool = ConnectedAgentTool(
       id=priority_agent.id,
       name=priority_agent_name,
       description="Assess the priority of a ticket"
   )

   team_agent_tool = ConnectedAgentTool(
       id=team_agent.id,
       name=team_agent_name,
       description="Determines which team should take the ticket"
   )

   effort_agent_tool = ConnectedAgentTool(
       id=effort_agent.id,
       name=effort_agent_name,
       description="Determines the effort required to complete the ticket"
   )
   ```

   Now you're ready to create a primary agent that will coordinate the ticket triage process, using the connected agents as required.

1. Find the comment **Create an agent to triage support ticket processing by using connected agents**, and enter the following code:

   ```python
   # Create an agent to triage support ticket processing by using connected agents
   triage_agent_name = "triage_agent-xxx"
   triage_agent_instructions = """
   Triage the given ticket. Use the connected tools to determine the ticket's priority,
   which team it should be assigned to, and how much effort it may take.
   """

   triage_agent = agents_client.create_agent(
       model=model_deployment,
       name=triage_agent_name,
       instructions=triage_agent_instructions,
       tools=[
           priority_agent_tool.definitions[0],
           team_agent_tool.definitions[0],
           effort_agent_tool.definitions[0]
       ]
   )
   ```

   > **Note**: Use the same suffix (first three letters of your first name) for this agent name.

   Now that you have defined a primary agent, you can submit a prompt to it and have it use the other agents to triage a support issue.

1. Find the comment **Use the agents to triage a support issue**, and enter the following code:

   ```python
   # Use the agents to triage a support issue
   print("Creating agent thread.")
   thread = agents_client.threads.create()

   # Create the ticket prompt
   prompt = input("\nWhat's the support problem you need to resolve?: ")

   # Send a prompt to the agent
   message = agents_client.messages.create(
       thread_id=thread.id,
       role=MessageRole.USER,
       content=prompt,
   )

   # Run the thread usng the primary agent
   print("\nProcessing agent thread. Please wait.")
   run = agents_client.runs.create_and_process(thread_id=thread.id, agent_id=triage_agent.id)

   if run.status == "failed":
       print(f"Run failed: {run.last_error}")

   # Fetch and display messages
   messages = agents_client.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)
   for message in messages:
       if message.text_messages:
           last_msg = message.text_messages[-1]
           print(f"{message.role}:\n{last_msg.text.value}\n")

   ```

1. Find the comment **Clean up**, and enter the following code to delete the agents when they are no longer required:

   ```python
   # Clean up
   print("Cleaning up agents:")
   agents_client.delete_agent(triage_agent.id)
   print("Deleted triage agent.")
   agents_client.delete_agent(priority_agent.id)
   print("Deleted priority agent.")
   agents_client.delete_agent(team_agent.id)
   print("Deleted team agent.")
   agents_client.delete_agent(effort_agent.id)
   print("Deleted effort agent.")
   ```

1. Save your changes to the code file. You can keep it open in case you need to edit the code to fix any errors.

### Run the app

Now you're ready to run your code and watch your AI agents collaborate.

1. In the terminal, enter the following command to run the application:

   ```
   python agent_triage.py
   ```

1. Enter a prompt, such as `Users can't reset their password from the mobile app.`

   After the agents process the prompt, you should see some output similar to the following:

   ```output
   Creating agent thread.
   Processing agent thread. Please wait.

   MessageRole.USER:
   Users can't reset their password from the mobile app.

   MessageRole.AGENT:
   ### Ticket Assessment

   - **Priority:** High — This issue blocks users from resetting their passwords, limiting access to their accounts.
   - **Assigned Team:** Frontend Team — The problem lies in the mobile app's user interface or functionality.
   - **Effort Required:** Medium — Resolving this problem involves identifying the root cause, potentially updating the mobile app functionality, reviewing API/backend integration, and testing to ensure compatibility across Android/iOS platforms.

   Cleaning up agents:
   Deleted triage agent.
   Deleted priority agent.
   Deleted team agent.
   Deleted effort agent.
   ```

   You can try modifying the prompt using a different ticket scenario to see how the agents collaborate. For example, "Investigate occasional 502 errors from the search endpoint."
