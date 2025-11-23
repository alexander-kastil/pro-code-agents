---
lab:
    title: 'Explore AI Agent development'
    description: 'Take your first steps in developing AI agents by exploring the Azure AI Agent service in the Microsoft Foundry portal.'
---

# Explore AI Agent development

In this exercise, you use the Azure AI Agent service in the Microsoft Foundry portal to create a simple AI agent that assists employees with expense claims.

This exercise takes approximately **30** minutes.

> **Note**: Some of the technologies used in this exercise are in preview or in active development. You may experience some unexpected behavior, warnings, or errors.

## Access the existing Foundry project

You'll use an existing Foundry project that has been pre-configured for this lab.

1. In a web browser, open the [Foundry portal](https://ai.azure.com) at `https://ai.azure.com` and sign in using your Azure credentials. Close any tips or quick start panes that are opened the first time you sign in, and if necessary use the **Foundry** logo at the top left to navigate to the home page, which looks similar to the following image (close the **Help** pane if it's open):

    ![Screenshot of Foundry portal.](./_images/ai-foundry-home.png)

   > **Important**: Make sure the **New Foundry** toggle is _Off_ for this lab.

1. In the home page, select **All resources** from the left navigation pane.
1. Locate and select the project named **pro-code-agents-student**.
1. In the left navigation menu, select **Agents**, then select **Create an agent** to open the Agents playground.

    ![Screenshot of a Foundry project Agents playground.](./_images/ai-foundry-agents-playground.png)

The project has several pre-deployed models available for use, including **gpt-4o**, **gpt-4o-mini**, **gpt-4.1-mini**, **gpt-5-mini**, and **text-embedding-ada-002**.

## Create your agent

Now you're ready to build an AI agent. In this exercise, you'll build a simple agent that answers questions based on a corporate expenses policy. You'll use the expenses policy document from the labfiles folder as _grounding_ data for the agent.

> **Note**: To avoid naming conflicts with other students, append the first three letters of your first name to agent names. For example, if your name is Alice, name your agent `ExpensesAgent-ali`.

1. Locate the **Expenses_Policy.docx** file in the `labs/PROCESSED/lab-01/labfiles/` folder in your development environment. This document contains details of the expenses policy for the fictional Contoso corporation.
1. In the Foundry Agents playground, find the **Setup** pane (it may be to the side or below the chat window).
1. Set the **Agent name** to `ExpensesAgent-xxx` (where `xxx` is the first three letters of your first name), ensure that the **gpt-4o** model deployment is selected, and set the **Instructions** to:

   ```prompt
   You are an AI assistant for corporate expenses.
   You answer questions about expenses based on the expenses policy data.
   If a user wants to submit an expense claim, you get their email address, a description of the claim, and the amount to be claimed and write the claim details to a text file that the user can download.
   ```

    ![Screenshot of the AI agent setup page in Foundry portal.](./_images/ai-agent-setup.png)

1. Further down in the **Setup** pane, next to the **Knowledge** header, select **+ Add**. Then in the **Add knowledge** dialog box, select **Files**.
1. In the **Adding files** dialog box, create a new vector store named `Expenses_Vector_Store`, uploading and saving the **Expenses_policy.docx** file from the labfiles folder.
1. In the **Setup** pane, in the **Knowledge** section, verify that **Expenses_Vector_Store** is listed and shown as containing 1 file.
1. Below the **Knowledge** section, next to **Actions**, select **+ Add**. Then in the **Add action** dialog box, select **Code interpreter** and then select **Save** (you do not need to upload any files for the code interpreter).

   Your agent will use the document you uploaded as its knowledge source to _ground_ its responses (in other words, it will answer questions based on the contents of this document). It will use the code interpreter tool as required to perform actions by generating and running its own Python code.

## Test your agent

Now that you've created an agent, you can test it in the playground chat.

1. In the playground chat entry, enter the prompt: `What's the maximum I can claim for meals?` and review the agent's response - which should be based on information in the expenses policy document you added as knowledge to the agent setup.

   > **Note**: If the agent fails to respond because the rate limit is exceeded. Wait a few seconds and try again. If there is insufficient quota available in your subscription, the model may not be able to respond. If the problem persists, try to increase the quota for your model on the **Models + endpoints** page.

1. Try the following follow-up prompt: `I'd like to submit a claim for a meal.` and review the response. The agent should ask you for the required information to submit a claim.
1. Provide the agent with an email address; for example, `fred@contoso.com`. The agent should acknowledge the response and request the remaining information required for the expense claim (description and amount)
1. Submit a prompt that describes the claim and the amount; for example, `Breakfast cost me $20`.
1. The agent should use the code interpreter to prepare the expense claim text file, and provide a link so you can download it.

    ![Screenshot of the Agent Playground in Foundry portal.](./_images/ai-agent-playground.png)

1. Download and open the text document to see the expense claim details.
