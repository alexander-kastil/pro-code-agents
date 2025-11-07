# Foundry SDK Python Demo

This demo shows how to use Azure AI Foundry SDK with Python.

## Setup

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Copy the template and configure your environment:

   ```bash
   cp config.json.template .env
   ```

3. Edit `.env` and set your `PROJECT_CONNECTION_STRING`:

   ```
   PROJECT_CONNECTION_STRING=your_connection_string_here
   ```

4. Run the demos:
   ```bash
   python chat-foundry.py
   python prompt-templates.py
   ```
