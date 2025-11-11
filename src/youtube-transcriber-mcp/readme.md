# YouTube Transcription MCP Server

A Model Context Protocol (MCP) server that provides YouTube video transcription capabilities using the FastMCP framework. This Python-based server exposes tools for extracting and retrieving transcriptions from YouTube videos, making it easy for AI agents and MCP clients to access video content programmatically. The server leverages the YouTube Transcript API through LangChain to support multiple languages and various YouTube URL formats.

## Description

The YouTube Transcriber MCP server implements a FastMCP server that provides transcription functionality for YouTube videos. It can extract video IDs from both standard YouTube URLs and shortened youtu.be links, then fetch and return the complete transcription text in the requested language.

## How to Run

1. **Set up the environment and install dependencies using uv:**

   ```bash
   uv venv
   uv pip install -r requirements.txt
   ```

2. **Activate the virtual environment:**

   ```bash
   # On Windows PowerShell:
   .venv\Scripts\Activate.ps1

   # On Linux/macOS:
   source .venv/bin/activate
   ```

3. **Start the MCP server:**

   ```bash
   python server.py
   ```

   The server will start on `http://127.0.0.1:8000/mcp`

   Alternatively, use the provided startup script:

   ```bash
   # On Windows:
   .\start.ps1

   # On Linux/macOS:
   ./start.sh
   ```
