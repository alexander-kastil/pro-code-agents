"""
Logging configuration module for connected agents.

This module provides centralized logging setup with:
- Color-coded output (yellow for INFO, white for DEBUG)
- Verbose mode control via parameters
- ANSI color support for Windows via colorama
- Mermaid diagram generation for agent interactions
"""

import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

# Optional ANSI color support on Windows
try:
    from colorama import init as _colorama_init  # type: ignore
    _colorama_init()
except Exception:
    pass


class ColoredFormatter(logging.Formatter):
    """
    Custom formatter that adds colors to log messages.
    - INFO messages: Yellow
    - DEBUG messages: White (default terminal color)
    - WARNING messages: Default
    - ERROR messages: Default
    """
    YELLOW = "\033[33m"
    WHITE = "\033[37m"
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        base = super().format(record)
        if record.levelno == logging.INFO:
            return f"{self.YELLOW}{base}{self.RESET}"
        elif record.levelno == logging.DEBUG:
            return f"{self.WHITE}{base}{self.RESET}"
        return base


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
                label = f"{msg_type}"
                if content:
                    # Truncate long content
                    if len(content) > 40:
                        content = content[:37] + "..."
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
        
        # Create markdown content with task description and diagram
        content_lines = []
        
        if self._user_prompt:
            content_lines.append(f"# Agent Interaction: {self._user_prompt}\n")
            content_lines.append(f"**Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        else:
            content_lines.append(f"# Agent Interaction\n")
            content_lines.append(f"**Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        content_lines.append("## Sequence Diagram\n")
        content_lines.append("```mermaid")
        content_lines.append(diagram)
        content_lines.append("```\n")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("\n".join(content_lines))
        
        logging.info(f"Mermaid diagram saved to: {filepath}")
    
    def clear(self):
        """Clear all collected events."""
        self._events.clear()
        self._participants.clear()
    
    @property
    def is_enabled(self) -> bool:
        """Return whether mermaid logging is enabled."""
        return self._enabled


class LoggingConfig:
    """
    Centralized logging configuration for the application.
    
    Handles:
    - Root logger setup with color formatting
    - Azure SDK logger configuration
    - Console clearing behavior
    - Mermaid diagram logging
    """
    
    def __init__(self):
        self._verbose = False
        self._azure_http_log = False
        self._mermaid_logger: Optional[MermaidLogger] = None
    
    def setup_logging(self, verbose: bool = False, azure_http_log: bool = False, create_mermaid: bool = False) -> logging.Logger:
        """
        Configure the root logger and Azure SDK loggers.
        
        Args:
            verbose: If True, sets level to DEBUG and shows both INFO (yellow) and DEBUG (white) messages.
                    If False, sets level to INFO and shows only INFO (yellow) messages.
            azure_http_log: If True, enables Azure SDK HTTP request/response logging.
                           If False, suppresses HTTP logs unless verbose is True.
            create_mermaid: If True, enables Mermaid diagram data collection.
        
        Returns:
            The configured root logger.
        """
        self._verbose = verbose
        self._azure_http_log = azure_http_log
        
        # Initialize Mermaid logger
        self._mermaid_logger = MermaidLogger(enabled=create_mermaid, verbose=verbose)
        
        logger = logging.getLogger()
        logger.handlers.clear()
        
        # Set log level based on verbosity
        log_level = logging.DEBUG if verbose else logging.INFO
        logger.setLevel(log_level)
        
        # Create console handler
        handler = logging.StreamHandler()
        handler.setLevel(log_level)
        
        # Set colored formatter
        formatter = ColoredFormatter("%(asctime)s [%(levelname)s] %(message)s")
        handler.setFormatter(formatter)
        
        logger.addHandler(handler)

        # Azure SDK logging configuration
        http_logger = logging.getLogger("azure.core.pipeline.policies.http_logging_policy")
        identity_logger = logging.getLogger("azure.identity")
        azure_logger = logging.getLogger("azure")

        # Suppress noisy HTTP logs unless explicitly enabled or in verbose mode
        if verbose or azure_http_log:
            http_logger.setLevel(logging.INFO)
        else:
            http_logger.setLevel(logging.WARNING)

        # Reduce general Azure SDK noise when not verbose
        if verbose:
            identity_logger.setLevel(logging.INFO)
            azure_logger.setLevel(logging.INFO)
        else:
            identity_logger.setLevel(logging.WARNING)
            azure_logger.setLevel(logging.WARNING)
        
        # Clear console unless verbose mode is enabled
        if not verbose:
            os.system('cls' if os.name == 'nt' else 'clear')
        
        return logger
    
    @property
    def is_verbose(self) -> bool:
        """Return whether verbose mode is enabled."""
        return self._verbose
    
    @property
    def mermaid_logger(self) -> Optional[MermaidLogger]:
        """Return the Mermaid logger instance."""
        return self._mermaid_logger


def vdebug(msg: str):
    """
    Convenience function for verbose debug logging.
    Always calls logging.debug(); visibility is controlled by logging level.
    """
    logging.debug(msg)
