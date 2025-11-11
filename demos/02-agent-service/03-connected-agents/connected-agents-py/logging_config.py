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
    
    def emit(self, record: logging.LogRecord):
        """Capture HTTP request/response logs."""
        if not self.mermaid_logger or not self.mermaid_logger._http_log:
            return
        
        message = record.getMessage()
        
        # Capture request method and URL
        if "Request method:" in message:
            self.current_request_method = message.split("'")[1] if "'" in message else None
        elif "Request URL:" in message and self.current_request_method:
            # Extract the endpoint path from the URL
            if "/assistants?" in message:
                endpoint = "/assistants"
            elif "/threads?" in message:
                endpoint = "/threads"
            elif "/messages?" in message:
                endpoint = "/messages"
            elif "/runs?" in message:
                endpoint = "/runs"
            elif "/assistants/" in message and "?" in message:
                endpoint = "/assistants/{id}"
            else:
                endpoint = message.split('/api/projects/')[1].split('?')[0] if '/api/projects/' in message else "unknown"
            
            self.current_request_url = f"{self.current_request_method} {endpoint}"
        elif "Response status:" in message and self.current_request_url:
            # Extract status code
            status = message.split("Response status:")[1].strip()
            
            # Add to HTTP events
            self.mermaid_logger.log_http_request(self.current_request_url, status)
            
            # Reset for next request
            self.current_request_method = None
            self.current_request_url = None


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
