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


class ColoredFormatter(logging.Formatter):
    """Simple colored formatter for INFO (yellow) and DEBUG (white)."""
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

        # Completely suppress Azure HTTP request/response logging in console
        try:
            http_logger.handlers.clear()
        except Exception:
            pass
        http_logger.propagate = False
        # Set to a level higher than CRITICAL and disable the logger
        http_logger.setLevel(logging.CRITICAL + 10)
        http_logger.disabled = True

        # Reduce general Azure SDK noise when not verbose
        if verbose:
            identity_logger.setLevel(logging.INFO)
            azure_logger.setLevel(logging.INFO)
        else:
            identity_logger.setLevel(logging.WARNING)
            azure_logger.setLevel(logging.WARNING)

        # Suppress HTTP chatter from common HTTP clients (urllib3, httpx)
        urllib3_logger = logging.getLogger("urllib3")
        urllib3_conn_logger = logging.getLogger("urllib3.connectionpool")
        httpx_logger = logging.getLogger("httpx")
        urllib3_logger.setLevel(logging.WARNING)
        urllib3_conn_logger.setLevel(logging.WARNING)
        httpx_logger.setLevel(logging.WARNING)
        
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
