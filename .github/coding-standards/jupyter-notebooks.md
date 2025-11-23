# Jupyter Notebook Coding Standards

## Overview

This document provides coding standards for creating educational Jupyter notebooks for agentic AI development. Notebooks should be clear, well-documented, and easy to follow for learners.

## Notebook Structure

### Standard Notebook Organization

1. **Title Cell**: Clear, descriptive title with context
2. **Table of Contents**: For notebooks with multiple sections
3. **Introduction**: Overview of what the notebook covers
4. **Setup Section**: Environment setup and imports
5. **Main Content**: Organized into logical sections
6. **Summary**: Key takeaways and next steps

### Example Notebook Structure

```python
# Cell 1: Title and Description
"""
# Prompt Engineering for Agentic AI

This notebook demonstrates prompt engineering techniques for working with
agentic AI models.

## Learning Objectives
- Understand basic prompt structures
- Learn prompt refinement techniques
- Apply chain-of-thought prompting
- Explore advanced patterns
"""

# Cell 2: Table of Contents
"""
## Table of Contents
1. [Introduction](#introduction)
2. [Environment Setup](#setup)
3. [Basic Prompt Structures](#basic-structures)
4. [Prompt Refinement Techniques](#refinement)
5. [Chain of Thought Prompting](#chain-of-thought)
6. [Summary and Best Practices](#summary)
"""

# Cell 3: Introduction
"""
## 1. Introduction <a id="introduction"></a>

### What is Prompt Engineering?

Prompt engineering is the practice of designing and optimizing inputs
to AI models to elicit desired responses.
"""

# Cell 4: Setup
"""
## 2. Environment Setup <a id="setup"></a>

First, we'll set up our environment and load necessary dependencies.
"""

# Cell 5: Imports
import os
from dotenv import load_dotenv
from azure.ai.inference import ChatCompletionsClient
from azure.identity import DefaultAzureCredential

# Cell 6: Configuration
# Load environment variables
load_dotenv()
endpoint = os.getenv("PROJECT_ENDPOINT")
model = os.getenv("MODEL_DEPLOYMENT")

print(f"✓ Environment configured")
print(f"  Endpoint: {endpoint}")
print(f"  Model: {model}")
```

## Markdown Guidelines

### Headers and Sections

Use clear, hierarchical headers:

```markdown
# Main Title (only one per notebook)

## Section Header

### Subsection Header

#### Minor Header (use sparingly)
```

### Explanatory Text

Write clear, concise explanations:

```markdown
## Understanding the Code

The following code demonstrates how to create a basic agent. We'll:

1. Initialize the Azure AI client
2. Create an agent with specific instructions
3. Start a conversation thread
4. Send a message and receive a response

Each step is explained in detail below.
```

### Code Explanations

Provide context before and after code cells:

```markdown
### Creating the Agent

We'll create an agent with specific instructions. The agent will act as
a helpful assistant.
```

```python
# Create the agent
agent = client.agents.create_agent(
    model=model,
    name="basic-agent",
    instructions="You are a helpful assistant that provides clear, concise answers."
)

print(f"Created agent: {agent.name}")
print(f"Agent ID: {agent.id}")
```

```markdown
**Output Explanation**: The agent is now created and ready to use.
Note the agent ID - we'll use this to interact with the agent.
```

### Lists and Bullets

Use lists for clarity:

```markdown
**Key Points:**
- Agents can be customized with specific instructions
- Each agent has a unique ID
- Agents can be reused across multiple conversations
- Instructions guide the agent's behavior and tone
```

### Call-Out Boxes

Use markdown quotes for important notes:

```markdown
> **Note**: Always store your API keys in environment variables,
> never hardcode them in your notebooks.

> **Best Practice**: Create a new thread for each distinct conversation
> to keep context clean.

> **Warning**: Large files may take time to process.
> Be patient when uploading documents.
```

## Code Cell Standards

### Imports Organization

Group imports logically:

```python
# Standard library imports
import os
import time
import json
from typing import List, Dict, Optional

# Third-party imports
from dotenv import load_dotenv
import pandas as pd
import matplotlib.pyplot as plt

# Azure SDK imports
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.inference import ChatCompletionsClient
```

### Clear Variable Names

Use descriptive variable names:

```python
# Good
user_message = "What is the weather today?"
agent_response = client.chat(user_message)
conversation_history = []

# Avoid
msg = "What is the weather today?"
resp = client.chat(msg)
hist = []
```

### Comments in Code

Add comments for complex logic:

```python
# Initialize the chat client with Azure credentials
client = ChatCompletionsClient(
    endpoint=endpoint,
    credential=DefaultAzureCredential()
)

# Create a list to store conversation history
# This helps maintain context across multiple interactions
conversation_history = []

# Helper function to format messages for display
def format_message(role: str, content: str) -> str:
    """Format a message for clean console output."""
    return f"{role.upper()}: {content}\n{'-' * 50}"
```

### Output Display

Format output for readability:

```python
# Display agent response
print("=" * 60)
print("AGENT RESPONSE")
print("=" * 60)
print(response.content)
print("=" * 60)

# Or use rich formatting
from IPython.display import display, Markdown

display(Markdown(f"### Agent Response\n\n{response.content}"))
```

## Interactive Examples

### User Input Cells

Create interactive examples:

```python
# Interactive example: Ask your own question
user_question = input("Enter your question: ")

response = agent.chat(user_question)
print(f"\nAgent: {response.content}")
```

### Visualization

Include visualizations when helpful:

```python
import matplotlib.pyplot as plt

# Visualize conversation length over time
conversation_lengths = [len(msg) for msg in conversation_history]

plt.figure(figsize=(10, 5))
plt.plot(conversation_lengths, marker='o')
plt.title('Conversation Message Length Over Time')
plt.xlabel('Message Number')
plt.ylabel('Message Length (characters)')
plt.grid(True)
plt.show()
```

### Progress Indicators

Show progress for long-running operations:

```python
from tqdm.notebook import tqdm
import time

# Process multiple documents with progress bar
documents = ["doc1.pdf", "doc2.pdf", "doc3.pdf"]

for doc in tqdm(documents, desc="Processing documents"):
    # Simulate processing
    result = process_document(doc)
    time.sleep(1)  # Simulate work
```

## Educational Best Practices

### Step-by-Step Progression

Build complexity gradually:

```python
# Step 1: Simple example
simple_prompt = "What is AI?"
response = client.chat(simple_prompt)
print(response.content)

# Step 2: Add context
context_prompt = """Context: You are teaching a beginner.
Question: What is AI?
Explain in simple terms."""
response = client.chat(context_prompt)
print(response.content)

# Step 3: Add structure
structured_prompt = """You are teaching a beginner about AI.

Question: What is AI?

Please structure your answer with:
1. A simple definition
2. A real-world example
3. Why it matters
"""
response = client.chat(structured_prompt)
print(response.content)
```

### Comparison Examples

Show before and after:

```python
# Example: Before optimization
basic_prompt = "Summarize this document"
basic_response = client.chat(basic_prompt)

# Example: After optimization
optimized_prompt = """Please provide a structured summary of the document:

1. Main Topic (1 sentence)
2. Key Points (3-5 bullet points)
3. Conclusion (1 sentence)

Keep the summary concise and actionable."""
optimized_response = client.chat(optimized_prompt)

# Compare results
print("BASIC APPROACH:")
print(basic_response.content)
print("\nOPTIMIZED APPROACH:")
print(optimized_response.content)
```

### Exercises

Include practice exercises:

```markdown
### Exercise 1: Create Your Own Agent

Try creating an agent with a different persona.
Experiment with these instructions:

1. A technical expert who explains concepts with code examples
2. A creative writer who tells stories
3. A data analyst who focuses on numbers and statistics

Modify the code below to create your custom agent:
```

```python
# Your code here
custom_agent = client.agents.create_agent(
    model=model,
    name="my-custom-agent",
    instructions="Your custom instructions here"
)

# Test your agent
test_response = custom_agent.chat("Tell me about machine learning")
print(test_response.content)
```

## Error Handling in Notebooks

### Graceful Error Messages

Handle errors with clear messages:

```python
try:
    # Attempt to create agent
    agent = client.agents.create_agent(
        model=model,
        name="test-agent",
        instructions="You are helpful"
    )
    print("✓ Agent created successfully")

except Exception as e:
    print("❌ Error creating agent:")
    print(f"   {str(e)}")
    print("\nTroubleshooting:")
    print("1. Check your PROJECT_ENDPOINT is correct")
    print("2. Verify MODEL_DEPLOYMENT exists")
    print("3. Ensure you're authenticated with Azure CLI")
```

### Checkpoint Cells

Add checkpoint cells to verify setup:

```python
# CHECKPOINT: Verify environment setup
print("Checking environment configuration...\n")

checks = {
    "Project Endpoint": endpoint is not None,
    "Model Deployment": model is not None,
    "Client Initialized": client is not None
}

all_passed = True
for check, status in checks.items():
    symbol = "✓" if status else "❌"
    print(f"{symbol} {check}: {'Configured' if status else 'Missing'}")
    if not status:
        all_passed = False

if all_passed:
    print("\n✓ All checks passed! Ready to proceed.")
else:
    print("\n❌ Please fix the issues above before continuing.")
```

## Notebook Metadata

### Cell Metadata

Use cell tags for organization:

```python
# In Jupyter, add cell tags: "setup", "example", "exercise", "cleanup"
```

### Requirements Cell

Include dependencies at the top:

````python
# Cell tagged as "requirements"
"""
## Required Packages

This notebook requires the following packages:
- azure-ai-projects>=1.0.0
- azure-ai-inference>=1.0.0
- azure-identity>=1.15.0
- python-dotenv>=1.0.0
- matplotlib>=3.7.0
- pandas>=2.0.0

Install with:
```bash
pip install -r requirements.txt
````

"""

````

## Summary Cell Template

```markdown
## Summary

### What We Learned

In this notebook, we covered:

- ✓ How to set up Azure AI clients
- ✓ Creating and configuring agents
- ✓ Managing conversation threads
- ✓ Handling agent responses
- ✓ Best practices for prompt engineering

### Key Takeaways

1. **Clear Instructions**: Agent instructions should be specific and actionable
2. **Context Management**: Use threads to maintain conversation context
3. **Error Handling**: Always validate configuration before making API calls
4. **Iterative Refinement**: Test and refine prompts for better results

### Next Steps

- Explore advanced agent features (tools, file search)
- Try multi-agent orchestration
- Implement agent workflows
- Build a production application

### Additional Resources

- [Azure AI Foundry Documentation](https://learn.microsoft.com/azure/ai-foundry)
- [Agent Service Guide](https://learn.microsoft.com/azure/ai-foundry/agents)
- [Best Practices for Agents](https://learn.microsoft.com/azure/ai-foundry/best-practices)
````

## Best Practices

### DO

- ✓ Use descriptive cell outputs
- ✓ Include learning objectives
- ✓ Provide clear explanations
- ✓ Show both code and results
- ✓ Add practice exercises
- ✓ Include error handling examples
- ✓ Use visualizations when helpful
- ✓ Add summary sections
- ✓ Include checkpoint cells

### DON'T

- ✗ Overcrowd cells with too much code
- ✗ Skip explanations for complex logic
- ✗ Assume prior knowledge without links
- ✗ Use unclear variable names
- ✗ Hide imports in the middle of notebooks
- ✗ Leave error messages unclear
- ✗ Forget to clean up resources
- ✗ Make cells dependent on execution order without noting it

## Testing Notebooks

Before sharing notebooks:

1. **Restart and Run All**: Ensure cells execute in order
2. **Clear Outputs**: Remove outputs with sensitive data
3. **Verify Links**: Check all documentation links work
4. **Test Examples**: Confirm all code examples run successfully
5. **Check Formatting**: Ensure markdown renders correctly
6. **Review Images**: Verify all images display properly

## Quick Reference

- Clear structure: Title → ToC → Setup → Content → Summary
- Progressive complexity in examples
- Comprehensive explanations in markdown cells
- Interactive examples with user input
- Checkpoint cells to verify setup
