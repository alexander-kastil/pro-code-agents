# Function Calling Python Demo

This demo shows how to use Azure AI Foundry SDK with Python for function calling.

## Setup

1. Install dependencies:

   ```bash
   uv sync
   ```

2. Copy the template and configure your environment:

   ```bash
   cp .env.copy .env
   ```

3. Edit `.env` and set your `PROJECT_ENDPOINT`, `OPENAI_API_VERSION`, and `MODEL`:

   ```
   PROJECT_ENDPOINT=https://your-ai-services-account-name.services.ai.azure.com/api/projects/your-project-name
   OPENAI_API_VERSION=2024-02-01
   MODEL="gpt-4.1-mini"
   ```

4. Run the demo:
   ```bash
   uv run python function-calling.py
   ```
