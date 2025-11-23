---
lab:
    title: 'Explore and compare language models'
    description: 'Generative AI applications are built on one or more language models. Learn how to find and compare models in the model catalog.'
---

# Explore and compare language models

The Microsoft Foundry model catalog serves as a central repository where you can explore and compare a variety of models, facilitating the selection of appropriate models for your generative AI scenario.

In this exercise, you'll explore the model catalog in Foundry portal, and compare potential models for a generative AI application that assists in solving problems.

This exercise will take approximately **25** minutes.

> **Note**: Some of the technologies used in this exercise are in preview or in active development. You may experience some unexpected behavior, warnings, or errors.

## Explore models

Let's start by signing into Foundry portal and exploring some of the available models.

1. In a web browser, open the [Foundry portal](https://ai.azure.com) at `https://ai.azure.com` and sign in using your Azure credentials. Close any tips or quick start panes that are opened the first time you sign in, and if necessary use the **Foundry** logo at the top left to navigate to the home page, which looks similar to the following image (close the **Help** pane if it's open):

   ![Screenshot of Foundry portal.](./_images-02/ai-foundry-home.png)

1. Review the information on the home page.
1. In the home page, in the **Explore models and capabilities** section, search for the `gpt-4o` model; which we'll use in our project.
1. In the search results, select the **gpt-4o** model to see its details.
1. Read the description and review the other information available on the **Details** tab.

   ![Screenshot of the gpt-4o model details page.](./_images-02/gpt4-details.png)

1. On the **gpt-4o** page, view the **Benchmarks** tab to see how the model compares across some standard performance benchmarks with other models that are used in similar scenarios.

   ![Screenshot of the gpt-4o model benchmarks page.](./_images-02/gpt4-benchmarks.png)

1. Use the back arrow (**&larr;**) next to the **gpt-4o** page title to return to the model catalog.
1. Search for `Phi-4-mini-instruct` and view the details and benchmarks for the **Phi-4-mini-instruct** model.

## Compare models

You've reviewed two different models, both of which could be used to implement a generative AI chat application. Now let's compare the metrics for these two models visually.

1. Use the back arrow (**&larr;**) to return to the model catalog.
1. Select **Compare models**. A visual chart for model comparison is displayed with a selection of common models.

   ![Screenshot of the model comparison page.](./_images-02/compare-models.png)

1. In the **Models to compare** pane, note that you can select popular tasks, such as _question answering_ to automatically select commonly used models for specific tasks.
1. Use the **Clear all models** (&#128465;) icon to remove all of the pre-selected models.
1. Use the **+ Model to compare** button to add the **gpt-4o** model to the list. Then use the same button to add the **Phi-4-mini-instruct** model to the list.
1. Review the chart, which compares the models based on **Quality Index** (a standardized score indicating model quality) and **Cost**. You can see the specific values for a model by holding the mouse over the point that represents it in the chart.

   ![Screenshot of the model comparison chart for gpt-4o and Phi-4-mini-instruct.](./_images-02/comparison-chart.png)

1. In the **X-axis** dropdown menu, under **Quality**, select the following metrics and observe each resulting chart before switching to the next:

   - Accuracy
   - Quality index

   Based on the benchmarks, the gpt-4o model looks like offering the best overall performance, but at a higher cost.

1. In the list of models to compare, select the **gpt-4o** model to re-open its benchmarks page.
1. In the page for the **gpt-4o** model page, select the **Overview** tab to view the model details.

## Access the existing project

To test models in the playground, you need to access a Foundry project. For this exercise, you will use the existing **pro-code-agents-student** project that has already been set up with the necessary model deployments.

1. In the navigation pane on the left, select **All projects**.
1. Locate and select the project named **pro-code-agents-student** from the list of available projects.
1. Once the project opens, in the navigation pane on the left, select **Playgrounds** and then open the **Chat playground**.

   ![Screenshot of a Foundry project chat playground.](./_images-02/ai-foundry-chat-playground.png)

## Chat with the _gpt-4o_ model

Now that you have access to the project with deployed models, you can use the playground to test them.

1. In the chat playground, in the **Setup** pane, ensure that your **gpt-4o** model is selected and in the **Give the model instructions and context** field, set the system prompt to `You are an AI assistant that helps solve problems.`
1. Select **Apply changes** to update the system prompt.

1. In the chat window, enter the following query

   ```
   I have a fox, a chicken, and a bag of grain that I need to take over a river in a boat. I can only take one thing at a time. If I leave the chicken and the grain unattended, the chicken will eat the grain. If I leave the fox and the chicken unattended, the fox will eat the chicken. How can I get all three things across the river without anything being eaten?
   ```

1. View the response. Then, enter the following follow-up query:

   ````
   Explain your reasoning.    ```
   ````

## Chat with the _Phi-4_ model

The **pro-code-agents-student** project also has the **Phi-4-mini-instruct** model deployed. Let's test this model in the playground.

1. In the navigation bar, ensure you're in the **Chat playground**.
1. In the chat playground, in the **Setup** pane, use the **Deployment** dropdown to select the **Phi-4-mini-instruct** model.
1. In the **Give the model instructions and context** field, set the system prompt to `You are an AI assistant that helps solve problems.` (the same system prompt you used to test the gpt-4o model).
1. Select **Apply changes** to update the system prompt and clear the chat history.
1. In the chat window, enter the following query

   ```
   I have a fox, a chicken, and a bag of grain that I need to take over a river in a boat. I can only take one thing at a time. If I leave the chicken and the grain unattended, the chicken will eat the grain. If I leave the fox and the chicken unattended, the fox will eat the chicken. How can I get all three things across the river without anything being eaten?
   ```

1. View the response. Then, enter the following follow-up query:

   ```
   Explain your reasoning.
   ```

## Perform a further comparison

1. Use the drop-down list in the **Setup** pane to switch between your models, testing both models with the following puzzle (the correct answer is 40!):

   ```
   I have 53 socks in my drawer: 21 identical blue, 15 identical black and 17 identical red. The lights are out, and it is completely dark. How many socks must I take out to make 100 percent certain I have at least one pair of black socks?
   ```

## Reflect on the models

You've compared two models, which may vary in terms of both their ability to generate appropriate responses and in their cost. In any generative scenario, you need to find a model with the right balance of suitability for the task you need it to perform and the cost of using the model for the number of requests you expect it to have to handle.

The details and benchmarks provided in the model catalog, along with the ability to visually compare models provides a useful starting point when identifying candidate models for a generative AI solution. You can then test candidate models with a variety of system and user prompts in the chat playground.

> **Note**: The **pro-code-agents-student** project and its resources are managed by your instructor. Do not delete any resources as they are shared with other students.
