# Azure AI Agent Service - Demo Presentations

This document contains structured content for creating PowerPoint presentations for each Azure AI Agent Service demo. Use this with M365 Copilot to generate individual presentations.

---

## Demo 1: Basic Agent

### Demo Name

**Basic Agent - Core Agent Lifecycle**

### Description

Demonstrates the fundamental lifecycle of an Azure AI Agent, including creation, thread management, message handling, and run execution with polling-based status checks.

### Key Elements

1. **Agent Creation** - Initialize agent with model and instructions using Microsoft Foundry
2. **Thread Management** - Create conversation threads to maintain context
3. **Message Creation** - Add user messages to threads with specific roles
4. **Run Execution** - Execute agent runs with polling-based status monitoring
5. **Response Handling** - Retrieve and display agent responses in conversation order

---

## Demo 2: Event Handler Agent

### Demo Name

**Event Handler Agent - Real-Time Streaming**

### Description

Implements custom event handling for real-time streaming responses from agents, enabling responsive user experiences through event-driven architecture.

### Key Elements

1. **Custom Event Handler** - Extend AgentEventHandler class for custom event processing
2. **Message Delta Streaming** - Receive and process text deltas as they arrive
3. **Event Lifecycle Hooks** - Handle thread messages, runs, and steps through callbacks
4. **Error Handling** - Implement on_error for graceful error management
5. **Stream Processing** - Use streaming API with event handlers for real-time responses

---

## Demo 3: Response Format Agent

### Demo Name

**Response Format Agent - Structured JSON Output**

### Description

Configures agents to return structured JSON responses instead of plain text, enabling programmatic processing and integration with downstream systems.

### Key Elements

1. **Response Format Configuration** - Set AgentsResponseFormat to json_object type
2. **Agent Instructions** - Guide agent to produce JSON-formatted responses
3. **Structured Data Request** - Request complex data (e.g., planet information)
4. **Run Status Validation** - Check RunStatus.COMPLETED for successful execution
5. **JSON Output Processing** - Receive and parse structured JSON from agent

---

## Demo 4: Image Input from URL

### Demo Name

**Image Input Agent - URL-based Vision**

### Description

Enables agents to analyze images from URLs, demonstrating multi-modal AI capabilities with vision-enabled models.

### Key Elements

1. **Vision Model Configuration** - Use vision-capable model (e.g., GPT-4 Vision)
2. **Multi-Modal Content Blocks** - Combine text and image URL in message content
3. **MessageImageUrlParam** - Configure image URL with detail level settings
4. **Image Analysis** - Process and describe visual content from remote images
5. **Mixed Content Handling** - Handle responses combining text and image analysis

---

## Demo 5: Image Input from File

### Demo Name

**Image Input Agent - File Upload Vision**

### Description

Demonstrates uploading local image files to Microsoft Foundry for agent analysis, enabling processing of local visual assets.

### Key Elements

1. **File Upload** - Use agents_client.files.upload_and_poll with FilePurpose.AGENTS
2. **Local File Handling** - Read and process local image files from assets
3. **MessageImageFileParam** - Reference uploaded file with file_id in messages
4. **Secure File Storage** - Store files temporarily in Microsoft Foundry
5. **File-Based Content Blocks** - Construct multi-modal messages with file references

---

## Demo 6: Image Input from Base64

### Demo Name

**Image Input Agent - Base64 Encoded Vision**

### Description

Processes images encoded as Base64 data URIs, enabling direct image transmission without file upload infrastructure.

### Key Elements

1. **Base64 Encoding** - Convert local images to Base64 strings
2. **Data URI Construction** - Create data:image/png;base64 formatted URLs
3. **Image Conversion Function** - Helper function for file-to-Base64 transformation
4. **Inline Image Transmission** - Send images directly in message content
5. **No File Upload Required** - Eliminate file storage for temporary image processing

---

## Demo 7: Agent Output to Storage

### Demo Name

**Agent Output - QR Code Generation & Storage**

### Description

Demonstrates agent output processing by generating QR codes from user input and storing them in Azure Blob Storage, showcasing integration with Azure services.

### Key Elements

1. **QR Code Generation** - Use qrcode library to create visual codes from text
2. **Azure Blob Storage Integration** - Upload generated images to cloud storage
3. **Dynamic Content Creation** - Generate artifacts based on user input
4. **Container Management** - Create and manage storage containers programmatically
5. **Public URL Generation** - Provide downloadable URLs for generated content

---

## Usage Instructions for M365 Copilot

To create a PowerPoint presentation for any demo:

1. Copy the relevant demo section (Demo Name, Description, and Key Elements)
2. Paste into M365 Copilot with a prompt like:

   ```
   Create a PowerPoint presentation with the following content:

   [Paste demo section here]

   Format:
   - Title slide with demo name
   - Overview slide with description
   - One slide per key element with visual examples
   - Summary/conclusion slide
   ```

3. Customize the generated presentation with:
   - Code snippets from the corresponding .py file
   - Architecture diagrams
   - Screenshots of output
   - Microsoft Foundry portal screenshots

---

## Additional Resources

- **Microsoft Learn Module**: [Develop an AI agent with Azure AI Agent Service](https://learn.microsoft.com/en-us/training/modules/develop-ai-agent-azure/)
- **Azure AI Documentation**: [Azure AI Agent Service Overview](https://learn.microsoft.com/en-us/azure/ai-services/agents/)
- **Python SDK Reference**: [azure-ai-agents PyPI](https://pypi.org/project/azure-ai-agents/)
