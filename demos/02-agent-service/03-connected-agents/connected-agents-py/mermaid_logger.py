"""
Mermaid diagram logger for agent interactions.

This module provides the MermaidLogger class for collecting and generating
Mermaid sequence diagrams from agent interaction events.
"""

import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from jinja2 import Environment, FileSystemLoader


class MermaidLogger:
    """
    Logger for collecting agent interaction events that can be used to generate Mermaid diagrams.
    
    Captures:
    - Agent invocations
    - Tool usages
    - Message exchanges between agents
    
    The collected data is structured to be easily translatable into Mermaid sequence diagram syntax.
    Supports three log levels: default, verbose, and http-log.
    """
    
    def __init__(self, enabled: bool = False, verbose: bool = False, http_log: bool = False):
        """
        Initialize the Mermaid logger.
        
        Args:
            enabled: Whether to collect mermaid diagram data
            verbose: Whether verbose output is enabled (affects what gets collected)
            http_log: Whether HTTP-level logging is enabled
        """
        self._enabled = enabled
        self._verbose = verbose
        self._http_log = http_log
        
        # Separate event collections for each log level
        self._default_events: List[Dict[str, Any]] = []
        self._verbose_events: List[Dict[str, Any]] = []
        self._http_events: List[Dict[str, Any]] = []
        
        self._participants: set = set()
        self._user_prompt: Optional[str] = None
        
        # Setup Jinja2 environment
        template_dir = os.path.join(os.path.dirname(__file__), 'templates')
        self._jinja_env = Environment(loader=FileSystemLoader(template_dir))
        
    def log_agent_creation(self, agent_name: str, agent_id: str):
        """Log the creation of an agent."""
        if not self._enabled:
            return
            
        self._participants.add(agent_name)
        event = {
            'type': 'agent_creation',
            'timestamp': datetime.now().isoformat(),
            'agent_name': agent_name,
            'agent_id': agent_id
        }
        
        # Default level: skip agent creation details
        # Verbose level: include agent creation
        self._verbose_events.append(event)
        
        if self._verbose:
            logging.debug(f"[Mermaid] Agent created: {agent_name} (id={agent_id})")
    
    def log_tool_registration(self, agent_name: str, tool_name: str):
        """Log the registration of a tool with an agent."""
        if not self._enabled:
            return
            
        self._participants.add(tool_name)
        event = {
            'type': 'tool_registration',
            'timestamp': datetime.now().isoformat(),
            'agent_name': agent_name,
            'tool_name': tool_name
        }
        
        # Default level: skip tool registration details
        # Verbose level: include tool registration
        self._verbose_events.append(event)
        
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
        
        # All log levels capture message events
        self._default_events.append(event)
        self._verbose_events.append(event)
        
        # HTTP log captures API-level communication
        if message_type in ['tool_call', 'tool_response', 'user_prompt', 'result']:
            self._http_events.append({
                'type': 'http_event',
                'timestamp': datetime.now().isoformat(),
                'description': f"API call: {from_entity} → {to_entity}",
                'details': f"{message_type}" + (f": {content_summary}" if content_summary else "")
            })
            
        if self._verbose:
            content_part = f": {content_summary}" if content_summary else ""
            logging.debug(f"[Mermaid] Message: {from_entity} -> {to_entity} ({message_type}){content_part}")
    
    def log_run_started(self, agent_name: str, thread_id: str):
        """Log when an agent run starts."""
        if not self._enabled:
            return
            
        event = {
            'type': 'run_started',
            'timestamp': datetime.now().isoformat(),
            'agent_name': agent_name,
            'thread_id': thread_id
        }
        
        # Default level: include run lifecycle
        self._default_events.append(event)
        self._verbose_events.append(event)
        
        if self._verbose:
            logging.debug(f"[Mermaid] Run started: {agent_name} on thread {thread_id}")
    
    def log_run_completed(self, agent_name: str, status: str):
        """Log when an agent run completes."""
        if not self._enabled:
            return
            
        event = {
            'type': 'run_completed',
            'timestamp': datetime.now().isoformat(),
            'agent_name': agent_name,
            'status': status
        }
        
        # Default level: include run lifecycle
        self._default_events.append(event)
        self._verbose_events.append(event)
        
        if self._verbose:
            logging.debug(f"[Mermaid] Run completed: {agent_name} (status={status})")
    
    def get_mermaid_diagram(self, log_level: str = 'default') -> str:
        """
        Generate a Mermaid sequence diagram from collected events.
        
        Args:
            log_level: Which log level to use ('default', 'verbose', or 'http')
        
        Returns:
            A string containing the Mermaid diagram syntax
        """
        if not self._enabled:
            return ""
        
        # Select event collection based on log level
        if log_level == 'verbose':
            events = self._verbose_events
        elif log_level == 'http':
            events = self._http_events
        else:
            events = self._default_events
            
        if not events:
            return ""
        
        lines = ["sequenceDiagram"]
        
        # Add participants
        for participant in sorted(self._participants):
            lines.append(f"    participant {participant}")
        
        # Add interactions
        for event in events:
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
    
    def _render_template(self, template_name: str, diagram: str, timestamp: str) -> str:
        """
        Render a Jinja2 template with diagram and metadata.
        
        Args:
            template_name: Name of the template file (e.g., 'default.md.j2')
            diagram: Mermaid sequence diagram content (no code fences)
            timestamp: Timestamp string used for the ticket and header
        
        Returns:
            Rendered markdown string
        """
        template = self._jinja_env.get_template(template_name)
        
        # Generate virtual ticket number based on timestamp
        ticket_number = f"TICKET-{timestamp}"
        
        context = {
            'ticket_number': ticket_number,
            'user_prompt': self._user_prompt or 'No description provided',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'diagram': diagram,
            'events': None,
            'http_events': None
        }
        
        # Add verbose events if rendering verbose template
        if template_name == 'verbose.md.j2':
            context['events'] = self._verbose_events
        
        # Add HTTP events if rendering HTTP template
        if template_name == 'http.md.j2':
            context['http_events'] = self._http_events
        
        return template.render(**context)

    def save_diagram(self, output_dir: Optional[str] = None):
        """
        Save the Mermaid diagrams to markdown files with timestamp and case description.
        Generates three separate files for default, verbose, and HTTP log levels.
        
        Args:
            output_dir: Directory to save the diagram files. If None, uses current directory.
        """
        if not self._enabled:
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
        
        # Prepare output directory
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        # Generate and save each log level diagram
        log_levels = [
            ('default', 'default.md.j2'),
            ('verbose', 'verbose.md.j2'),
            ('http', 'http.md.j2')
        ]
        
        for level_name, template_name in log_levels:
            diagram = self.get_mermaid_diagram(log_level=level_name)
            
            # Skip if no diagram content (only applies to http level if not enabled)
            if not diagram and level_name == 'http':
                # For HTTP level, still generate the file to show it's available
                diagram = "sequenceDiagram\n    Note over User: No HTTP events captured"
            
            if diagram:
                filename = f"{case_name}_{timestamp}_{level_name}.md"
                
                if output_dir:
                    filepath = os.path.join(output_dir, filename)
                else:
                    filepath = filename
                
                # Render template with Jinja2
                markdown_output = self._render_template(
                    template_name=template_name,
                    diagram=diagram,
                    timestamp=timestamp
                )
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(markdown_output)
                
                logging.info(f"Mermaid diagram ({level_name}) saved to: {filepath}")
    
    def clear(self):
        """Clear all collected events."""
        self._default_events.clear()
        self._verbose_events.clear()
        self._http_events.clear()
        self._participants.clear()
    
    @property
    def is_enabled(self) -> bool:
        """Return whether mermaid logging is enabled."""
        return self._enabled
