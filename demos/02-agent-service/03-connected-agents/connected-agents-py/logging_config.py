"""
Logging configuration module for connected agents.

This module provides centralized logging setup with:
- Color-coded output (yellow for INFO, white for DEBUG)
- Verbose mode control via parameters
- ANSI color support for Windows via colorama
"""

import os
import logging
from typing import Optional

from mermaid_logger import MermaidLogger

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


class HttpLogHandler(logging.Handler):
    """Custom handler to capture HTTP logs and add them to Mermaid logger."""
    
    def __init__(self, mermaid_logger: Optional[MermaidLogger] = None):
        super().__init__()
        self.mermaid_logger = mermaid_logger
        self.current_request_method = None
        self.current_request_url = None
        self.current_endpoint = None
    
    def _parse_endpoint(self, url: str) -> str:
        """
        Parse and normalize the endpoint from a full URL.
        
        Args:
            url: Full URL string
            
        Returns:
            Normalized endpoint path
        """
        try:
            # Extract the path after /api/projects/{project_id}/
            if '/api/projects/' in url:
                # Split on /api/projects/ and get the part after
                parts = url.split('/api/projects/')
                if len(parts) > 1:
                    # Get everything after the project ID, before query parameters
                    path_with_params = parts[1]
                    # Remove query parameters
                    path = path_with_params.split('?')[0]
                    
                    # Split into segments
                    segments = path.split('/')
                    
                    # Skip the project ID (first segment)
                    if len(segments) > 1:
                        resource_path = '/'.join(segments[1:])
                        
                        # Normalize common patterns
                        # Replace UUIDs and IDs with placeholders
                        normalized_segments = []
                        for i, segment in enumerate(resource_path.split('/')):
                            # Check if segment looks like an ID
                            # IDs are typically:
                            # - Very long (>20 chars) like UUIDs
                            # - Or contain hyphens and are reasonably long (>8 chars) like "thread-abc123"
                            # - Or start with common prefixes like "asst_", "thread_", "run_", "msg_"
                            is_id = (
                                len(segment) > 20 or
                                (len(segment) > 8 and '-' in segment) or
                                (len(segment) > 8 and '_' in segment and 
                                 any(segment.startswith(prefix) for prefix in ['asst', 'thread', 'run', 'msg', 'agent']))
                            )
                            
                            if is_id:
                                normalized_segments.append('{id}')
                            else:
                                normalized_segments.append(segment)
                        
                        return '/' + '/'.join(normalized_segments)
            
            return 'unknown'
        except Exception:
            return 'unknown'
    
    def emit(self, record: logging.LogRecord):
        """Capture HTTP request/response logs."""
        if not self.mermaid_logger or not self.mermaid_logger._http_log:
            return
        
        message = record.getMessage()
        
        # Capture request method
        if "Request method:" in message:
            # Extract method from message like "Request method: 'POST'"
            try:
                self.current_request_method = message.split("'")[1]
            except (IndexError, AttributeError):
                self.current_request_method = None
                
        # Capture request URL
        elif "Request URL:" in message and self.current_request_method:
            # Extract URL from message like "Request URL: 'https://...'"
            try:
                url = message.split("'")[1]
                self.current_endpoint = self._parse_endpoint(url)
                self.current_request_url = f"{self.current_request_method} {self.current_endpoint}"
            except (IndexError, AttributeError):
                self.current_request_url = None
                self.current_endpoint = None
                
        # Capture response status
        elif "Response status:" in message and self.current_request_url:
            # Extract status from message like "Response status: 201"
            try:
                status = message.split("Response status:")[1].strip()
                
                # Add to HTTP events with full details
                self.mermaid_logger.log_http_request(
                    request=self.current_request_url,
                    status=status,
                    endpoint=self.current_endpoint
                )
                
            except (IndexError, AttributeError):
                pass
            finally:
                # Always reset for next request
                self.current_request_method = None
                self.current_request_url = None
                self.current_endpoint = None


class LogUtil:
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
        self._mermaid_logger = MermaidLogger(enabled=create_mermaid, verbose=verbose, http_log=azure_http_log)
        
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

        # Add HTTP log handler for Mermaid diagram capture
        if create_mermaid and azure_http_log:
            http_capture_handler = HttpLogHandler(self._mermaid_logger)
            http_capture_handler.setLevel(logging.INFO)
            http_logger.addHandler(http_capture_handler)

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
