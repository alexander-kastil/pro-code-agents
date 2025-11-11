# Mermaid Diagram Generation

This feature allows you to collect agent interaction events and generate Mermaid sequence diagrams to visualize the agent workflow.

## Configuration

Enable Mermaid diagram generation by setting the environment variable in `.env`:

```
CREATE_MERMAID_DIAGRAM=true
```

## How It Works

When enabled, the `MermaidLogger` class collects events during agent execution:

- Agent creations
- Tool registrations  
- Message exchanges
- Agent run lifecycle (start/complete)

## Output

When the script completes, it automatically saves a Mermaid diagram to `agent_interactions.mmd` in the current directory.

## Viewing the Diagram

You can view the generated Mermaid diagram using:

1. **Online**: Copy the content of `agent_interactions.mmd` to https://mermaid.live/
2. **VS Code**: Install the "Mermaid Preview" extension
3. **GitHub**: Mermaid diagrams are automatically rendered in markdown files

## Example Diagram

```mermaid
sequenceDiagram
    participant User
    participant triage-agent
    participant priority_agent
    participant team_agent
    participant effort_agent
    
    Note over priority_agent: Created
    Note over team_agent: Created
    Note over effort_agent: Created
    Note over triage-agent: Created
    
    User->triage-agent: user_prompt: Ticket content
    activate triage-agent
    
    triage-agent->>priority_agent: tool_call
    priority_agent-->>triage-agent: tool_response
    
    triage-agent->>team_agent: tool_call
    team_agent-->>triage-agent: tool_response
    
    triage-agent->>effort_agent: tool_call
    effort_agent-->>triage-agent: tool_response
    
    Note over triage-agent: completed
    deactivate triage-agent
    
    triage-agent->User: result: Triaged ticket
```

## Verbose Mode

When `VERBOSE_OUTPUT=true` is also set, the MermaidLogger will output debug messages showing each event as it's collected.
