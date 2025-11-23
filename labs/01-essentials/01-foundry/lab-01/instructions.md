---
lab:
    title: 'Explore an AI development project'
    description: 'Learn how to navigate and explore Microsoft Foundry projects that are set up for building AI solutions.'
---

# Explore an AI development project

In this exercise, you use Microsoft Foundry portal to explore an existing project and its resources.

This exercise takes approximately **30** minutes.

> **Note**: Some of the technologies used in this exercise are in preview or in active development. You may experience some unexpected behavior, warnings, or errors.

## Open Microsoft Foundry portal

Let's start by signing into Foundry portal.

1. In a web browser, open the [Foundry portal](https://ai.azure.com) at `https://ai.azure.com` and sign in using your Azure credentials. Close any tips or quick start panes that are opened the first time you sign in, and if necessary use the **Foundry** logo at the top left to navigate to the home page, which looks similar to the following image (close the **Help** pane if it's open):

   ![Screenshot of Foundry portal.](./_images/ai-foundry-home.png)

1. Review the information on the home page.

## Access the existing project

An Azure AI _project_ provides a collaborative workspace for AI development. For this exercise, you will use an existing project called **pro-code-agents-student** that has already been set up with the necessary models and resources.

> **Note**: AI Foundry projects can be based on an _Foundry_ resource, which provides access to AI models (including Azure OpenAI), Azure AI services, and other resources for developing AI agents and chat solutions. Alternatively, projects can be based on _AI hub_ resources; which include connections to Azure resources for secure storage, compute, and specialized tools. Foundry based projects are great for developers who want to manage resources for AI agent or chat app development. AI hub based projects are more suitable for enterprise development teams working on complex AI solutions.

1. In the navigation pane on the left, select **All projects**.
1. Locate and select the project named **pro-code-agents-student** from the list of available projects.
1. Once the project opens, review the project overview page:

   ![Screenshot of a Foundry project overview page.](./_images/ai-foundry-project.png)

1. At the bottom of the navigation pane on the left, select **Management center**. The management center is where you can view settings at both the _resource_ and _project_ levels; which are both shown in the navigation pane.

   ![Screenshot of the Management center page in Foundry portal.](./_images/ai-foundry-management.png)

   The _resource_ level relates to the **Foundry** resource that was created to support your project. This resource includes connections to Azure AI Services and Foundry models; and provides a central place to manage user access to AI development projects.

   The _project_ level relates to your individual project, where you can view project-specific resources.

1. In the navigation pane, in the section for your Foundry resource, select the **Overview** page to view its details.
1. Select the link to the **Resource group** associated with the resource to open a new browser tab and navigate to the Azure portal. Sign in with your Azure credentials if prompted.
1. View the resource group in the Azure portal to see the Azure resources that have been created to support your Foundry resource and your project.

   ![Screenshot of a Foundry resource and project resources in the Azure portal.](./_images/azure-portal-resources.png)

1. Close the Azure portal tab and return to the Foundry portal.

## Review project endpoints

The Foundry project includes a number of _endpoints_ that client applications can use to connect to the project and the models and AI services it includes.

1. In the Management center page, in the navigation pane, under your project, select **Go to project**.
1. In the project **Overview** page, view the **Endpoints and keys** section; which contains endpoints and authorization keys that you can use in your application code to access:
   - The Foundry project and any models deployed in it.
   - Azure OpenAI in Foundry models.
   - Azure AI services

## Test a generative AI model

Now that you know something about the configuration of the Foundry project, you can use the chat playground to explore the models available in the project.

1. In the navigation pane on the left for your project, select **Playgrounds**
1. Open the **Chat playground**, and ensure that the **gpt-4o** model deployment is selected in the **Deployment** section.
1. In the **Setup** pane, in the **Give the model instructions and context** box, enter the following instructions:

   ```
   You are a history teacher who can answer questions about past events all around the world.
   ```

1. Apply the changes to update the system message.
1. In the chat window, enter a query such as `What are the key events in the history of Scotland?` and view the response:

   ![Screenshot of the playground in Foundry portal.](./_images/ai-foundry-playground.png)

## Summary

In this exercise, you've explored Foundry, and seen how to navigate and explore an existing project and its related resources.

> **Note**: The **pro-code-agents-student** project and its resources are managed by your instructor. Do not delete any resources as they are shared with other students.
