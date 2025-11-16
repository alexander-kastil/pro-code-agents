# Presentation Input: Azure AI Agent Service Demos

## agent-basics.py

### Slide 1: Objective

- Show minimal end-to-end agent lifecycle: create agent, thread, message, run, poll, list messages.
- Establish mental model of Threads (conversation state) and Runs (execution cycles).

### Slide 2: Key Concepts & APIs

- Classes: `AgentsClient` / `AIProjectClient.agents`, `threads.create`, `messages.create`, `runs.create`/`runs.get`.
- Poll pattern: run status transitions (queued → in_progress → completed/failed).
- Message roles: user vs assistant; retrieval ordering (`ListSortOrder`).

### Slide 3: Required Skills

- Environment & credentials (DefaultAzureCredential).
- Basic Python scripting & async avoidance for clarity.
- Reading SDK object models and iterating results.

## agent-event-handler.py

### Slide 1: Objective

- Demonstrate streaming and event-driven handling for granular lifecycle insight.

### Slide 2: Key Concepts & APIs

- `AgentEventHandler` callbacks: message delta, run step, run status, final completion.
- Streaming iterator (`runs.stream`) yields (event_type, event_data, handler return).

### Slide 3: Required Skills

- Understanding of callback pattern & iterator consumption.
- Interpreting incremental token/step events.
- Deciding when streaming vs polling suits UX/performance.

## agent-response-format.py

### Slide 1: Objective

- Enforce structured (JSON) output for reliable downstream parsing.

### Slide 2: Key Concepts & APIs

- `AgentsResponseFormat(type="json_object")` parameter in `create_agent`.
- Agent responds with machine-readable schema-like JSON instead of free-form text.

### Slide 3: Required Skills

- Recognizing when structured responses reduce parsing errors.
- Mapping model output to data pipelines.
- Basic JSON validation mindset.

## agent-input-file.py

### Slide 1: Objective

- Provide a local image file as multimodal input to the agent.

### Slide 2: Key Concepts & APIs

- File upload: `files.upload_and_poll(purpose=FilePurpose.AGENTS)`.
- Mixed content blocks: `MessageInputTextBlock` + `MessageInputImageFileBlock`.

### Slide 3: Required Skills

- Local file handling & path management.
- Multi-modal message composition semantics.
- Purpose scoping for uploaded artifacts.

## agent-input-url.py

### Slide 1: Objective

- Use an external image URL instead of an uploaded file.

### Slide 2: Key Concepts & APIs

- `MessageImageUrlParam(detail="high")` + `MessageInputImageUrlBlock`.
- Trade-offs: bandwidth, latency, hosting control vs convenience.

### Slide 3: Required Skills

- Evaluating image source strategies (file vs URL).
- Managing external resource reliability.
- Understanding vision model detail parameters.

## agent-input-base64.py

### Slide 1: Objective

- Embed image data inline via Base64 data URL for portability.

### Slide 2: Key Concepts & APIs

- Conversion function: read binary → `base64.b64encode` → data URL.
- Reuse of URL image block (`MessageInputImageUrlBlock`) for inline data.

### Slide 3: Required Skills

- Base64 encoding basics & size considerations.
- Choosing inline embedding vs storage reference.
- Multi-modal payload assembly.

## agent-output.py

### Slide 1: Objective

- Chain agent response into application logic (QR generation + Blob upload).

### Slide 2: Key Concepts & APIs

- Post-run message inspection; capturing assistant text.
- QR code creation (`qrcode` + Pillow); blob storage (`BlobServiceClient`).

### Slide 3: Required Skills

- Integrating AI output with external services.
- Binary data handling (in-memory bytes, uploads).
- Simple artifact naming/versioning practices.

## Cross-Demo Skill Progression (Optional Overview Slide)

- Start: Core agent lifecycle & synchronous polling.
- Advance: Streaming events & structured output enforcement.
- Expand: Multi-modal inputs (file, URL, Base64).
- Integrate: External resource workflows & artifact persistence.
