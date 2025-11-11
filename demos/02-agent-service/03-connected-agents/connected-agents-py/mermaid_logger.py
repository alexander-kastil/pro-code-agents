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
        # Only active levels will have data collected
        self._default_events: List[Dict[str, Any]] = []
        self._verbose_events: List[Dict[str, Any]] = []
        self._http_events: List[Dict[str, Any]] = []
        
        self._participants: set = set()
        self._user_prompt: Optional[str] = None
        
        # Token usage tracking
        self._total_tokens_in: int = 0
        self._total_tokens_out: int = 0
        
        # Triage results tracking
        self._triage_result: Optional[str] = None
        
        # Setup Jinja2 environment
        template_dir = os.path.join(os.path.dirname(__file__), 'templates')
        self._jinja_env = Environment(loader=FileSystemLoader(template_dir))
    
    @property
    def active_log_levels(self) -> List[str]:
        """Return list of active log levels based on configuration."""
        levels = ['default']  # Always active
        if self._verbose:
            levels.append('verbose')
        return levels
        
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
        
        # Only verbose level includes agent creation details
        if self._verbose:
            self._verbose_events.append(event)
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
        
        # Only verbose level includes tool registration details
        if self._verbose:
            self._verbose_events.append(event)
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
        
        # Capture the triage result (agent's final response)
        if message_type == 'result' and from_entity == 'triage-agent' and content_summary:
            self._triage_result = content_summary
            
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
        
        # Default level: always collect message events
        self._default_events.append(event)
        
        # Verbose level: collect if enabled
        if self._verbose:
            self._verbose_events.append(event)
        
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
        
        # Verbose level: collect if enabled
        if self._verbose:
            self._verbose_events.append(event)
            logging.debug(f"[Mermaid] Run started: {agent_name} on thread {thread_id}")
    
    def log_http_request(self, request: str, status: str, endpoint: Optional[str] = None):
        """
        Log an HTTP request/response for the HTTP level diagram.
        
        Args:
            request: The HTTP request (e.g., "POST /assistants")
            status: The HTTP response status code
            endpoint: The endpoint path (e.g., "/assistants")
        """
        if not self._enabled or not self._http_log:
            return
        
        event = {
            'type': 'http_request',
            'timestamp': datetime.now().isoformat(),
            'request': request,
            'status': status
        }
        
        if endpoint:
            event['endpoint'] = endpoint
        
        self._http_events.append(event)
        
        logging.debug(f"[Mermaid] HTTP: {request} -> {status}")
    
    def log_run_completed(self, agent_name: str, status: str, usage: Optional[Dict[str, Any]] = None):
        """
        Log when an agent run completes.
        
        Args:
            agent_name: Name of the agent
            status: Status of the run
            usage: Optional usage statistics with prompt_tokens, completion_tokens, total_tokens
        """
        if not self._enabled:
            return
            
        event = {
            'type': 'run_completed',
            'timestamp': datetime.now().isoformat(),
            'agent_name': agent_name,
            'status': status
        }
        
        # Track token usage if provided
        if usage:
            event['usage'] = usage
            self._total_tokens_in += usage.get('prompt_tokens', 0)
            self._total_tokens_out += usage.get('completion_tokens', 0)
        
        # Default level: include run lifecycle
        self._default_events.append(event)
        
        # Verbose level: collect if enabled
        if self._verbose:
            self._verbose_events.append(event)
            if usage:
                logging.debug(f"[Mermaid] Run completed: {agent_name} (status={status}, tokens={usage})")
            else:
                logging.debug(f"[Mermaid] Run completed: {agent_name} (status={status})")
    
    def get_mermaid_diagram(self, log_level: str = 'default') -> str:
        """
        Generate a Mermaid diagram from collected events.
        
        Args:
            log_level: Which log level to use ('default', 'verbose', or 'http')
        
        Returns:
            A string containing the Mermaid diagram syntax
        """
        if not self._enabled:
            return ""
        
        # Route to appropriate diagram generator based on level
        if log_level == 'verbose':
            return self._generate_verbose_flowchart()
        elif log_level == 'http':
            return self._generate_http_timeline()
        else:
            return self._generate_default_sequence()
    
    def _generate_default_sequence(self) -> str:
        """Generate sequence diagram for default log level."""
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
            
            elif event['type'] == 'run_started':
                agent_name = event['agent_name']
                lines.append(f"    activate {agent_name}")
            
            elif event['type'] == 'run_completed':
                agent_name = event['agent_name']
                status = event['status']
                lines.append(f"    Note over {agent_name}: {status}")
                lines.append(f"    deactivate {agent_name}")
        
        return "\n".join(lines)
    
    def _generate_verbose_flowchart(self) -> str:
        """Generate flowchart for verbose log level showing setup and execution flow."""
        events = self._verbose_events
        if not events:
            return ""
        
        lines = ["graph TD"]
        
        # Track agents and tools
        agents_created = []
        tools_registered = {}
        
        for event in events:
            if event['type'] == 'agent_creation':
                agent_name = event['agent_name']
                agents_created.append(agent_name)
            elif event['type'] == 'tool_registration':
                agent_name = event['agent_name']
                tool_name = event['tool_name']
                if agent_name not in tools_registered:
                    tools_registered[agent_name] = []
                tools_registered[agent_name].append(tool_name)
        
        # Build flowchart
        lines.append("    Start([System Start])")
        
        # Agent creation phase
        for i, agent in enumerate(agents_created):
            node_id = f"Agent{i}"
            lines.append(f"    {node_id}[Create {agent}]")
            if i == 0:
                lines.append(f"    Start --> {node_id}")
            else:
                lines.append(f"    Agent{i-1} --> {node_id}")
        
        # Tool registration phase
        if tools_registered:
            last_agent_id = f"Agent{len(agents_created)-1}"
            lines.append(f"    ToolReg{{Tool Registration}}")
            lines.append(f"    {last_agent_id} --> ToolReg")
            
            for agent, tools in tools_registered.items():
                for tool in tools:
                    safe_tool = tool.replace('-', '_').replace(' ', '_')
                    lines.append(f"    Tool_{safe_tool}[{tool}]")
                    lines.append(f"    ToolReg --> Tool_{safe_tool}")
        
        # Execution phase
        lines.append("    Exec[Execute Triage]")
        if tools_registered:
            lines.append("    ToolReg --> Exec")
        else:
            lines.append(f"    Agent{len(agents_created)-1} --> Exec")
        
        lines.append("    Complete([Complete])")
        lines.append("    Exec --> Complete")
        
        return "\n".join(lines)
    
    def _generate_http_timeline(self) -> str:
        """Generate detailed HTTP sequence diagram showing actual API calls."""
        events = self._http_events
        if not events:
            return ""
        
        # Create detailed sequence diagram showing HTTP interactions
        lines = ["sequenceDiagram"]
        lines.append("    participant Client as Client App")
        lines.append("    participant API as Azure AI Agent Service")
        
        # Track sequential request numbers for better visualization
        request_num = 1
        
        for event in events:
            if event['type'] == 'http_request':
                request = event.get('request', '')
                status = event.get('status', '')
                endpoint = event.get('endpoint', '')
                
                # Parse request to get method and endpoint
                if ' ' in request:
                    method, endpoint_path = request.split(' ', 1)
                    
                    # Create descriptive labels based on endpoint
                    operation = self._get_operation_description(method, endpoint_path)
                    
                    # Determine if it's a request or response based on method
                    if method in ['POST', 'GET', 'DELETE', 'PUT', 'PATCH']:
                        # Add activation box for POST/DELETE operations that create/modify resources
                        if method in ['POST', 'DELETE']:
                            lines.append(f"    activate API")
                        
                        # Request arrow with numbered label
                        lines.append(f"    Client->>+API: [{request_num}] {method} {endpoint_path}")
                        
                        # Add note with operation description if available
                        if operation:
                            lines.append(f"    Note right of API: {operation}")
                        
                        # Response arrow with status code
                        status_emoji = self._get_status_emoji(status)
                        lines.append(f"    API-->>-Client: {status} {status_emoji}")
                        
                        # Deactivate if we activated earlier
                        if method in ['POST', 'DELETE']:
                            lines.append(f"    deactivate API")
                        
                        request_num += 1
        
        return "\n".join(lines)
    
    def _get_operation_description(self, method: str, endpoint: str) -> str:
        """
        Get a human-readable description of the API operation.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            
        Returns:
            Description of the operation
        """
        # Normalize endpoint by removing trailing segments that are IDs
        normalized = endpoint
        
        # Map common endpoint patterns to descriptions
        # Order matters - more specific patterns first
        patterns = [
            # Assistants (agents)
            (r'/assistants/{id}', {
                'GET': 'Get agent details',
                'DELETE': 'Delete agent',
                'PATCH': 'Update agent'
            }),
            (r'/assistants', {
                'POST': 'Create agent',
                'GET': 'List agents'
            }),
            # Threads with nested resources
            (r'/threads/{id}/runs/{id}', {
                'GET': 'Get run status',
                'DELETE': 'Cancel run'
            }),
            (r'/threads/{id}/runs', {
                'POST': 'Start run',
                'GET': 'List runs'
            }),
            (r'/threads/{id}/messages', {
                'POST': 'Add message',
                'GET': 'List messages'
            }),
            (r'/threads/{id}', {
                'GET': 'Get thread',
                'DELETE': 'Delete thread'
            }),
            (r'/threads', {
                'POST': 'Create thread',
                'GET': 'List threads'
            }),
            # Standalone resources
            (r'/messages', {
                'POST': 'Create message',
                'GET': 'List messages'
            }),
            (r'/runs/{id}', {
                'GET': 'Get run status',
                'DELETE': 'Cancel run'
            }),
            (r'/runs', {
                'POST': 'Create run',
                'GET': 'List runs'
            })
        ]
        
        # Try to match the endpoint pattern
        for pattern, methods in patterns:
            # Simple pattern matching - check if the normalized endpoint matches
            if pattern == normalized or ('{id}' in pattern and self._matches_pattern(endpoint, pattern)):
                return methods.get(method, '')
        
        return ''
    
    def _matches_pattern(self, endpoint: str, pattern: str) -> bool:
        """
        Check if an endpoint matches a pattern with {id} placeholders.
        
        Args:
            endpoint: Actual endpoint path
            pattern: Pattern with {id} placeholders
            
        Returns:
            True if the endpoint matches the pattern
        """
        # Known resource names that should NOT be treated as IDs
        resource_names = {'messages', 'runs', 'threads', 'assistants', 'files', 'steps'}
        
        # Split both into parts
        endpoint_parts = endpoint.split('/')
        pattern_parts = pattern.split('/')
        
        # Must have same number of parts
        if len(endpoint_parts) != len(pattern_parts):
            return False
        
        # Check each part
        for ep, pp in zip(endpoint_parts, pattern_parts):
            if pp == '{id}':
                # This part should be an ID-like string, not a known resource name
                if ep in resource_names:
                    return False
                # Continue - we accept this as a potential ID
                continue
            elif ep != pp:
                return False
        
        return True
    
    def _get_status_emoji(self, status: str) -> str:
        """
        Get an emoji/symbol for HTTP status codes.
        
        Args:
            status: HTTP status code as string
            
        Returns:
            Emoji or symbol representing the status
        """
        try:
            status_code = int(status.split()[0])  # Handle "201 Created" format
            
            if 200 <= status_code < 300:
                return '✓'
            elif 300 <= status_code < 400:
                return '↪'
            elif 400 <= status_code < 500:
                return '⚠'
            elif 500 <= status_code < 600:
                return '✗'
        except (ValueError, IndexError):
            pass
        
        return ''
    
    def _render_template(self, timestamp: str) -> str:
        """
        Render a combined Jinja2 template with all active log level diagrams.
        
        Args:
            timestamp: Timestamp string used for the ticket and header
        
        Returns:
            Rendered markdown string with sections for each active log level
        """
        template = self._jinja_env.get_template('combined.md.j2')
        
        # Generate virtual ticket number based on timestamp
        ticket_number = f"TICKET-{timestamp}"
        
        # Collect diagrams for active log levels
        diagrams = {}
        for level in self.active_log_levels:
            diagram = self.get_mermaid_diagram(log_level=level)
            if diagram:
                diagrams[level] = diagram
        
        context = {
            'ticket_number': ticket_number,
            'user_prompt': self._user_prompt or 'No description provided',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'diagrams': diagrams,
            'active_levels': self.active_log_levels,
            'tokens_in': self._total_tokens_in,
            'tokens_out': self._total_tokens_out,
            'tokens_total': self._total_tokens_in + self._total_tokens_out,
            'triage_result': self._triage_result
        }
        
        return template.render(**context)

    def save_diagram(self, output_dir: Optional[str] = None):
        """
        Save a combined Mermaid diagram markdown file with sections for all active log levels.
        Only generates one file containing diagrams for currently active log levels.
        
        Args:
            output_dir: Directory to save the diagram file. If None, uses current directory.
        """
        if not self._enabled:
            return
        
        # Generate timestamp and ticket number
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        ticket_number = f"TICKET-{timestamp}"
        
        # Use ticket number as filename
        filename = f"{ticket_number}.md"
        
        # Prepare output directory
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            filepath = os.path.join(output_dir, filename)
        else:
            filepath = filename
        
        # Render combined template with all active log levels
        markdown_output = self._render_template(timestamp=timestamp)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(markdown_output)
        
        levels_str = ', '.join(self.active_log_levels)
        logging.info(f"Mermaid diagram saved to: {filepath} (levels: {levels_str})")
    
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
