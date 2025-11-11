"""
Mermaid diagram logger for agent interactions.

This module provides the MermaidLogger class for collecting and generating
Mermaid sequence diagrams from agent interaction events.
"""

import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime


class MermaidLogger:
    """
    Logger for collecting agent interaction events that can be used to generate Mermaid diagrams.
    
    Captures:
    - Agent invocations
    - Tool usages
    - Message exchanges between agents
    
    The collected data is structured to be easily translatable into Mermaid sequence diagram syntax.
    """
    
    def __init__(self, enabled: bool = False, verbose: bool = False):
        """
        Initialize the Mermaid logger.
        
        Args:
            enabled: Whether to collect mermaid diagram data
            verbose: Whether verbose output is enabled (affects what gets collected)
        """
        self._enabled = enabled
        self._verbose = verbose
        self._events: List[Dict[str, Any]] = []
        self._participants: set = set()
        self._user_prompt: Optional[str] = None
        
    def log_agent_creation(self, agent_name: str, agent_id: str):
        """Log the creation of an agent."""
        if not self._enabled:
            return
            
        self._participants.add(agent_name)
        self._events.append({
            'type': 'agent_creation',
            'timestamp': datetime.now().isoformat(),
            'agent_name': agent_name,
            'agent_id': agent_id
        })
        
        if self._verbose:
            logging.debug(f"[Mermaid] Agent created: {agent_name} (id={agent_id})")
    
    def log_tool_registration(self, agent_name: str, tool_name: str):
        """Log the registration of a tool with an agent."""
        if not self._enabled:
            return
            
        self._participants.add(tool_name)
        self._events.append({
            'type': 'tool_registration',
            'timestamp': datetime.now().isoformat(),
            'agent_name': agent_name,
            'tool_name': tool_name
        })
        
        if self._verbose:
            logging.debug(f"[Mermaid] Tool registered: {tool_name} -> {agent_name}")
    
    def log_message_sent(self, from_entity: str, to_entity: str, message_type: str, content_summary: Optional[str] = None):
        """
        Log a message sent between entities (user, agent, tool).
        
        Args:
            from_entity: The sender (e.g., 'User', 'triage-agent')
            to_entity: The receiver (e.g., 'priority_agent', 'Thread')
            message_type: Type of message (e.g., 'user_prompt', 'tool_call', 'tool_response')
            content_summary: Brief summary of the content (optional)
        """
        if not self._enabled:
            return
        
        # Capture the user prompt for later use in filename/documentation
        if message_type == 'user_prompt' and from_entity == 'User' and content_summary:
            self._user_prompt = content_summary
            
        self._participants.add(from_entity)
        self._participants.add(to_entity)
        
        event = {
            'type': 'message',
            'timestamp': datetime.now().isoformat(),
            'from': from_entity,
            'to': to_entity,
            'message_type': message_type
        }
        
        if content_summary:
            event['content'] = content_summary
            
        self._events.append(event)
        
        if self._verbose:
            content_part = f": {content_summary}" if content_summary else ""
            logging.debug(f"[Mermaid] Message: {from_entity} -> {to_entity} ({message_type}){content_part}")
    
    def log_run_started(self, agent_name: str, thread_id: str):
        """Log when an agent run starts."""
        if not self._enabled:
            return
            
        self._events.append({
            'type': 'run_started',
            'timestamp': datetime.now().isoformat(),
            'agent_name': agent_name,
            'thread_id': thread_id
        })
        
        if self._verbose:
            logging.debug(f"[Mermaid] Run started: {agent_name} on thread {thread_id}")
    
    def log_run_completed(self, agent_name: str, status: str):
        """Log when an agent run completes."""
        if not self._enabled:
            return
            
        self._events.append({
            'type': 'run_completed',
            'timestamp': datetime.now().isoformat(),
            'agent_name': agent_name,
            'status': status
        })
        
        if self._verbose:
            logging.debug(f"[Mermaid] Run completed: {agent_name} (status={status})")
    
    def get_mermaid_diagram(self) -> str:
        """
        Generate a Mermaid sequence diagram from collected events.
        
        Returns:
            A string containing the Mermaid diagram syntax
        """
        if not self._enabled or not self._events:
            return ""
        
        lines = ["sequenceDiagram"]
        
        # Add participants
        for participant in sorted(self._participants):
            lines.append(f"    participant {participant}")
        
        # Add interactions
        for event in self._events:
            if event['type'] == 'message':
                from_entity = event['from']
                to_entity = event['to']
                msg_type = event['message_type']
                content = event.get('content', '')
                
                # Format the message label
                # For result messages, omit the content to avoid markdown syntax issues
                if msg_type == 'result':
                    label = msg_type
                else:
                    label = f"{msg_type}"
                    if content:
                        # Truncate long content and sanitize for Mermaid
                        if len(content) > 40:
                            content = content[:37] + "..."
                        # Remove characters that can break Mermaid syntax
                        content = content.replace('#', '').replace('*', '').replace('-', '').strip()
                        if content:  # Only add content if there's something left after sanitizing
                            label = f"{msg_type}: {content}"
                
                # Use different arrow types based on message type
                if msg_type in ['tool_call', 'delegation']:
                    lines.append(f"    {from_entity}->>{to_entity}: {label}")
                elif msg_type in ['tool_response', 'result']:
                    lines.append(f"    {to_entity}-->>{from_entity}: {label}")
                else:
                    lines.append(f"    {from_entity}->{to_entity}: {label}")
            
            elif event['type'] == 'agent_creation':
                agent_name = event['agent_name']
                lines.append(f"    Note over {agent_name}: Created")
            
            elif event['type'] == 'run_started':
                agent_name = event['agent_name']
                lines.append(f"    activate {agent_name}")
            
            elif event['type'] == 'run_completed':
                agent_name = event['agent_name']
                status = event['status']
                lines.append(f"    Note over {agent_name}: {status}")
                lines.append(f"    deactivate {agent_name}")
        
        return "\n".join(lines)
    
    def _compose_markdown(self, diagram: str, timestamp: str) -> str:
        """
        Compose the markdown report content for a ticket, placing the
        non-technical description first, followed by the technical details
        and the Mermaid diagram.

        Args:
            diagram: Mermaid sequence diagram content (no code fences)
            timestamp: Timestamp string used for the ticket and header

        Returns:
            A markdown string
        """
        # Create markdown content with task description and diagram
        content_lines: List[str] = []

        # Generate virtual ticket number based on timestamp
        ticket_number = f"TICKET-{timestamp}"

        if self._user_prompt:
            content_lines.append(f"# {ticket_number}\n")
            content_lines.append(f"**Description:** {self._user_prompt}\n")
            content_lines.append(f"**Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        else:
            content_lines.append(f"# {ticket_number}\n")
            content_lines.append(f"**Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        # Outcome (non-technical summary) first
        content_lines.append("## Outcome\n")
        content_lines.append("The ticket was processed through a multi-agent triage system where specialized agents analyzed different aspects:\n")
        content_lines.append("- **Priority Agent**: Assessed urgency based on impact and user-facing issues\n")
        content_lines.append("- **Team Agent**: Determined optimal team assignment based on ticket content\n")
        content_lines.append("- **Effort Agent**: Estimated required work and complexity\n")
        content_lines.append("\nThe main orchestrator agent coordinated these assessments to provide comprehensive triage results.\n")

        # Technical section after the outcome
        content_lines.append("## Technical Process\n")
        content_lines.append("The triage agent used connected agents as tools. Each specialized agent operates independently with its own instructions, while the main agent delegates tasks and aggregates responses.\n")
        content_lines.append("### Agent Interaction Diagram\n")
        content_lines.append("```mermaid")
        content_lines.append(diagram)
        content_lines.append("```\n")

        return "\n".join(content_lines)

    def save_diagram(self, output_dir: Optional[str] = None):
        """
        Save the Mermaid diagram to a markdown file with timestamp and case description.
        
        Args:
            output_dir: Directory to save the diagram file. If None, uses current directory.
        """
        if not self._enabled:
            return
            
        diagram = self.get_mermaid_diagram()
        if not diagram:
            return
        
        # Generate filename with case description and timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create a safe filename from the user prompt
        if self._user_prompt:
            # Take first few words of prompt for filename
            case_name = "_".join(self._user_prompt.split()[:5])
            # Remove special characters
            case_name = "".join(c if c.isalnum() or c in ('_', '-') else '_' for c in case_name)
            case_name = case_name[:50]  # Limit length
        else:
            case_name = "case"
        
        filename = f"{case_name}_{timestamp}.md"
        
        # Prepare output directory
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            filepath = os.path.join(output_dir, filename)
        else:
            filepath = filename
        
        # Compose markdown in a dedicated helper to keep save_diagram lean
        markdown_output = self._compose_markdown(diagram=diagram, timestamp=timestamp)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(markdown_output)
        
        logging.info(f"Mermaid diagram saved to: {filepath}")
    
    def clear(self):
        """Clear all collected events."""
        self._events.clear()
        self._participants.clear()
    
    @property
    def is_enabled(self) -> bool:
        """Return whether mermaid logging is enabled."""
        return self._enabled
