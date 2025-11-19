# Resources

## MS Learn

[Create custom copilots with Azure AI Studio](https://learn.microsoft.com/en-us/training/paths/create-custom-copilots-ai-studio/)

[Develop AI agents on Azure](https://learn.microsoft.com/en-us/training/paths/develop-ai-agents-on-azure/)

## GitHub

[Guide: Build your code-first agent with Azure AI Foundry](https://microsoft.github.io/build-your-first-agent-with-azure-ai-agent-service-workshop/)

[Python AI Agent Frameworks Demos](https://github.com/Azure-Samples/python-ai-agent-frameworks-demos)

## Articles

[Introducing agentic retrieval in Azure AI Search](https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/introducing-agentic-retrieval-in-azure-ai-search/4414677)

[Achieve End-to-End Observability in Azure AI Foundry](https://devblogs.microsoft.com/foundry/achieve-end-to-end-observability-in-azure-ai-foundry/)

[Announcing Microsoft Entra Agent ID: Secure and manage your AI agents](https://techcommunity.microsoft.com/blog/microsoft-entra-blog/announcing-microsoft-entra-agent-id-secure-and-manage-your-ai-agents/3827392)

## Research Papers

### Reasoning and Prompting Techniques

[Chain-of-Thought Prompting Elicits Reasoning in Large Language Models](https://arxiv.org/abs/2201.11903)
- Introduces Chain-of-Thought prompting for step-by-step reasoning
- Published by Google Research, 2022
- Foundational work for deep reasoning techniques

[Self-Consistency Improves Chain of Thought Reasoning](https://arxiv.org/abs/2203.11171)
- Improves CoT accuracy through multiple reasoning paths and majority voting
- Google Research, 2022
- Used in deep-reasoning.ipynb notebook

[Tree of Thoughts: Deliberate Problem Solving with Large Language Models](https://arxiv.org/abs/2305.10601)
- Extends CoT to explore multiple reasoning paths
- Princeton University & Google DeepMind, 2023
- Demonstrated in deep-reasoning.ipynb

[Least-to-Most Prompting Enables Complex Reasoning in Large Language Models](https://arxiv.org/abs/2205.10625)
- Breaking complex problems into simpler sub-problems
- Google Research, 2022
- Applied in deep-reasoning.ipynb

### Agent Frameworks

[ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629)
- Interleaves reasoning traces with task-specific actions
- Princeton University & Google Research, 2022
- Core framework implemented in react-framework.ipynb
- **Why it's important**: Foundation for modern autonomous agent systems

## Additional Resources Created for This Course

### Notebooks in demos/01-essentials/02-agentic-ai/01-prompt-engineering/

1. **agentic-rag.ipynb** - Agentic Retrieval-Augmented Generation
   - Demonstrates autonomous RAG systems with dynamic query planning
   - Implements query reformulation, self-reflection, and adaptive retrieval
   - Uses in-memory knowledge base for demonstration (no external dependencies)
   
2. **deep-reasoning.ipynb** - Deep Reasoning with LLMs
   - Implements Chain-of-Thought, Tree of Thoughts, Self-Consistency
   - Demonstrates Least-to-Most prompting and self-verification
   - All examples work with Azure AI Foundry deployed models
   
3. **react-framework.ipynb** - ReAct Framework Implementation
   - Complete implementation of Reasoning and Acting pattern
   - Includes tool usage, error handling, and self-reflection
   - Uses simple in-memory tools (no external APIs required)

### Why These Resources

These notebooks were created to provide hands-on learning for:
- **Agentic RAG**: Understanding how agents can autonomously manage retrieval strategies
- **Deep Reasoning**: Exploring advanced reasoning techniques beyond basic prompting
- **ReAct Framework**: Learning the foundation of modern autonomous agent systems

All notebooks are self-contained and use:
- Azure AI Foundry for LLM access
- In-memory knowledge bases (no external databases needed)
- Simple tools for demonstration purposes
- Production-ready patterns that can be extended

### Setup Requirements

All three notebooks require:
- Azure AI Foundry project with deployed model (gpt-4 or similar)
- Python packages: azure-ai-projects, azure-ai-inference, azure-identity, python-dotenv
- .env file with PROJECT_ENDPOINT and MODEL configured

No additional resources (databases, search services, etc.) are required for the demonstrations.
