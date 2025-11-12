"""
Logging configuration module for connected agents.

This module provides centralized logging setup with:
- Color-coded output (yellow for INFO, white for DEBUG)
- Verbose mode control via parameters
- ANSI color support for Windows via colorama
"""

import os
import logging

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


class LoggingConfig:
    """
    Centralized logging configuration for the application.
    
    Handles:
    - Root logger setup with color formatting
    - Azure SDK logger configuration
    - Console clearing behavior
    """
    
    def __init__(self):
        self._verbose = False
    
    def setup_logging(self, verbose: bool = False) -> logging.Logger:
        """
        Configure the root logger and Azure SDK loggers.
        
        Args:
            verbose: If True, sets level to DEBUG and shows both INFO (yellow) and DEBUG (white) messages.
                    If False, sets level to INFO and shows only INFO (yellow) messages.
        
        Returns:
            The configured root logger.
        """
        self._verbose = verbose
        
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

        # Suppress noisy HTTP logs unless in verbose mode
        if verbose:
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


def vdebug(msg: str):
    """
    Convenience function for verbose debug logging.
    Always calls logging.debug(); visibility is controlled by logging level.
    """
    logging.debug(msg)
