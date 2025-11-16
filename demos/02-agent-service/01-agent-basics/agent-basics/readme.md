# Azure AI Agent Service Basics

This C# console application demonstrates the core capabilities of Azure AI Agent Service, organized into multiple interactive demos.

## Demo Scripts Overview

| Demo                | Focus                                  | What It Demonstrates                                                                                                                                                                                                        |
| ------------------- | -------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `Basics`            | Core lifecycle                         | Creates an agent, a thread, sends a user message, starts a run, polls status, and lists messages. Shows the minimal synchronous workflow for interacting with Azure AI Agents and how statuses transition until completion. |
| `EventHandler`      | Streaming events                       | Introduces an event handler to stream granular lifecycle events (run state, step creation, message deltas). Demonstrates incremental token delivery and how to inspect event payloads without waiting for full completion.  |
| `ResponseFormat`    | Structured output                      | Configures the agent to return a JSON-formatted response via `AgentsResponseFormat`. Illustrates enforcing structured data (e.g. list of planets) suitable for downstream parsing. Highlights response format control.      |
| `InputFile`         | File input (image)                     | Uploads a local image file and passes it alongside text in a single multi-modal message. Shows file upload with purpose `AGENTS`, constructing mixed content blocks, and processing model vision capabilities.              |
| `InputUrl`          | URL image input                        | Uses a public image URL with detail level control instead of an uploaded file. Demonstrates sending external resource references directly and contrasts with file-based ingestion.                                          |
| `InputBase64`       | Data URL image input                   | Converts an image to Base64 and sends it as a `data:` URL. Shows an alternative for inline embedding when direct file upload or external hosting is not desired. Reinforces multi-modal message construction patterns.      |
| `Output`            | Post-processing & external integration | Runs an agent, captures its response, then generates a QR code and uploads it to Azure Blob Storage. Demonstrates chaining agent output into application logic and persisting artifacts externally.                         |

## Prerequisites

- .NET 10 SDK
- Azure AI Foundry project with configured AI Agent Service
- Azure credentials configured (via DefaultAzureCredential)
- Optional: Azure Storage account for the Output demo

## Configuration

Edit `appsettings.json` to configure your Azure resources:

| Setting                    | Description                                      | Required |
| -------------------------- | ------------------------------------------------ | -------- |
| `ProjectConnectionString`  | Azure AI Foundry project connection string       | Yes      |
| `Model`                    | Deployment name for the AI model (e.g. gpt-4o-mini) | Yes      |
| `StorageConnectionString`  | Azure Storage connection string                  | No*      |
| `StorageContainerName`     | Container name for blob storage                  | No*      |

*Required only for the Output demo

## Running the Application

1. Navigate to the project directory:
   ```bash
   cd demos/02-agent-service/01-agent-basics/agent-basics
   ```

2. Restore dependencies:
   ```bash
   dotnet restore
   ```

3. Run the application:
   ```bash
   dotnet run
   ```

4. Select a demo from the interactive menu by entering a number (1-7)

5. After each demo completes, press any key to return to the menu

6. Press Ctrl+C to exit the application

## Key Concepts Demonstrated

- **Agent Lifecycle**: Creating agents, threads, messages, and managing run states
- **Synchronous vs Streaming**: Polling for completion vs real-time event streaming
- **Multi-modal Input**: Text, images from files, URLs, and Base64-encoded data
- **Response Formatting**: Structured JSON output for downstream processing
- **External Integration**: Post-processing agent responses and uploading to Azure Storage

## Project Structure

```
agent-basics/
├── Models/
│   └── AppConfig.cs              # Configuration model
├── Services/
│   ├── AgentRunnerBasics.cs      # Core lifecycle demo
│   ├── AgentRunnerEventHandler.cs # Streaming events demo
│   ├── AgentRunnerResponseFormat.cs # Structured output demo
│   ├── AgentRunnerInputFile.cs   # File input demo
│   ├── AgentRunnerInputUrl.cs    # URL input demo
│   ├── AgentRunnerInputBase64.cs # Base64 input demo
│   └── AgentRunnerOutput.cs      # External integration demo
├── assets/
│   └── soi.jpg                   # Sample image for demos
├── Program.cs                     # Main entry point with menu
├── appsettings.json               # Configuration file
└── agent-basics.csproj            # Project file
```
