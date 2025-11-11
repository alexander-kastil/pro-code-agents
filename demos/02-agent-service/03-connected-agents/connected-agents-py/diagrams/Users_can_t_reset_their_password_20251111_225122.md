# Agent Interaction: Users can't reset their password from the mobile app.

**Timestamp:** 2025-11-11 22:51:22

## Sequence Diagram

```mermaid
sequenceDiagram
    participant User
    participant connected_supervisor_agent
    participant effort_agent
    participant priority_agent
    participant triage-agent
    Note over priority_agent: Created
    Note over connected_supervisor_agent: Created
    Note over effort_agent: Created
    Note over triage-agent: Created
    User->triage-agent: user_prompt: Users can't reset their password from...
    activate triage-agent
    Note over triage-agent: RunStatus.COMPLETED
    deactivate triage-agent
    User-->>triage-agent: result: ### Ticket Triage Summary

- **Priori...
```
