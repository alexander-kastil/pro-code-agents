# Prompt Engineering for Agentic AI

This folder contains a comprehensive Jupyter notebook demonstrating prompt engineering techniques for working with agentic AI models using Azure AI Foundry.

## Contents

- `prompt-engineering.ipynb` - Interactive Jupyter notebook with examples and exercises
- `requirements.txt` - Python dependencies
- `.env.copy` - Environment configuration template
- `setup.sh` - Setup script for Linux/macOS
- `setup.ps1` - Setup script for Windows PowerShell
- `.gitignore` - Git ignore rules for virtual environment and generated files

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Azure AI Foundry project with a deployed model
- Azure credentials configured for authentication

### Setup Instructions

#### Option 1: Using the Setup Script (Linux/macOS)

```bash
# Make the script executable (if not already)
chmod +x setup.sh

# Run the setup script
./setup.sh

# Activate the virtual environment
source .venv/bin/activate

# Copy the environment template and configure your credentials
cp .env.copy .env
# Edit .env with your Azure AI Foundry project details

# Launch Jupyter
jupyter notebook prompt-engineering.ipynb
```

#### Option 2: Using the Setup Script (Windows PowerShell)

```powershell
# Run the setup script
.\setup.ps1

# Activate the virtual environment
.\.venv\Scripts\Activate.ps1

# Copy the environment template and configure your credentials
Copy-Item .env.copy .env
# Edit .env with your Azure AI Foundry project details

# Launch Jupyter
jupyter notebook prompt-engineering.ipynb
```

#### Option 3: Manual Setup

```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.copy .env
# Edit .env with your credentials

# Launch Jupyter
jupyter notebook prompt-engineering.ipynb
```

### Configuration

Edit the `.env` file with your Azure AI Foundry project details:

```env
PROJECT_ENDPOINT="https://your-project.openai.azure.com/"
OPENAI_API_VERSION="2024-02-01"
MODEL="gpt-4.1-mini"
```

You can find these values in your Azure AI Foundry project settings.

## Notebook Topics

The notebook covers the following prompt engineering techniques:

### 1. Introduction to Prompt Engineering
- What is prompt engineering and why it matters
- Importance for agentic AI systems

### 2. Basic Prompt Structures
- Vague vs. specific prompts
- Role-based prompting
- Output format control

### 3. Prompt Refinement Techniques
- Few-shot learning (zero-shot vs. few-shot)
- Using delimiters and structure
- Temperature control for creativity vs. consistency

### 4. Chain of Thought Prompting
- Basic chain of thought
- Few-shot chain of thought
- Self-consistency techniques

### 5. Advanced Patterns
- Instruction following with constraints
- Iterative refinement through conversation
- Meta-prompting (asking AI to improve prompts)

### 6. Best Practices Summary
- Key principles of effective prompt engineering
- Best practices for agentic AI
- Practical exercises

## Key Features

- **Interactive Examples**: Each concept includes side-by-side comparisons showing how different prompts affect model responses
- **Helper Functions**: Pre-built functions for testing prompts and displaying comparisons
- **Real-world Scenarios**: Practical examples relevant to building AI agents
- **Practice Exercises**: Hands-on activities to reinforce learning

## Learning Objectives

After completing this notebook, you will be able to:

1. Understand the fundamentals of prompt engineering for AI models
2. Design effective prompts for different use cases
3. Apply chain of thought reasoning to complex problems
4. Use few-shot learning to improve model consistency
5. Control model output through temperature and constraints
6. Iterate and refine prompts for optimal results

## Troubleshooting

### Virtual Environment Issues
- Make sure Python 3.8+ is installed: `python3 --version`
- If activation fails, try: `python3 -m venv --clear .venv`

### Connection Issues
- Verify your `.env` file has the correct values
- Ensure Azure credentials are configured (run `az login` if using Azure CLI)
- Check that your model deployment is active in Azure AI Foundry

### Jupyter Issues
- If Jupyter doesn't start, ensure it's installed: `pip install jupyter`
- Try using JupyterLab instead: `jupyter lab prompt-engineering.ipynb`

## Additional Resources

- [Azure AI Foundry Documentation](https://learn.microsoft.com/azure/ai-studio/)
- [OpenAI Best Practices for Prompt Engineering](https://platform.openai.com/docs/guides/prompt-engineering)
- [Prompt Engineering Guide](https://www.promptingguide.ai/)

## Contributing

This is a training material. If you find issues or have suggestions for improvements, please discuss with the course instructor.
