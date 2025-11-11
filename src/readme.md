# Source Projects

This directory contains sample projects demonstrating various technologies and integrations.

## Projects Overview

| Project                                               | Language   | Description                                                   | Purpose                                                                                                                                               |
| ----------------------------------------------------- | ---------- | ------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| [currency-converter](./currency-converter/)           | TypeScript | Azure Functions API for currency conversion                   | Demonstrates building serverless HTTP APIs with Azure Functions, integrating with external REST APIs (Fixer.io) for real-time currency exchange rates |
| [youtube-transcriber-mcp](./youtube-transcriber-mcp/) | Python     | Model Context Protocol (MCP) server for YouTube transcription | Demonstrates building MCP servers using FastMCP framework, integrating with YouTube Transcript API to provide transcription capabilities to AI agents |

## Quick Start

### Currency Converter

```bash
cd currency-converter
npm install
npm start
```

### YouTube Transcriber MCP

```bash
cd youtube-transcriber-mcp
uv venv
uv pip install -r requirements.txt
python server.py
```

For detailed instructions on running and testing each project, please refer to their individual README files.
