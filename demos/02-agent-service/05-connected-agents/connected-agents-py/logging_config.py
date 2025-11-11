"""
Logging configuration module for connected agents.

This module provides centralized logging setup with:
- Color-coded output (yellow for INFO, white for DEBUG)
- Verbose mode control via VERBOSE_OUTPUT environment variable
- ANSI color support for Windows via colorama
"""

import os
import logging
from dotenv import load_dotenv

# Load environment variables early
load_dotenv()

# Determine verbosity: only VERBOSE_OUTPUT=="true" enables verbose (DEBUG) output
_verbose_value = os.getenv("VERBOSE_OUTPUT", "false")
VERBOSE = _verbose_value == "true"

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


def setup_logging():
    """
    Configure the root logger with appropriate settings.
    
    If VERBOSE_OUTPUT is "true":
        - Sets level to DEBUG
        - Shows both INFO (yellow) and DEBUG (white) messages
    
    If VERBOSE_OUTPUT is "false" or any other value:
        - Sets level to INFO
        - Shows only INFO (yellow) messages, DEBUG messages are hidden
    """
    logger = logging.getLogger()
    logger.handlers.clear()
    
    # Set log level based on verbosity
    log_level = logging.DEBUG if VERBOSE else logging.INFO
    logger.setLevel(log_level)
    
    # Create console handler
    handler = logging.StreamHandler()
    handler.setLevel(log_level)
    
    # Set colored formatter
    formatter = ColoredFormatter("%(asctime)s [%(levelname)s] %(message)s")
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    
    # Clear console unless verbose mode is enabled
    if not VERBOSE:
        os.system('cls' if os.name == 'nt' else 'clear')
    
    return logger


def get_verbose_status():
    """Return whether verbose mode is enabled."""
    return VERBOSE


def vdebug(msg: str):
    """
    Convenience function for verbose debug logging.
    Always calls logging.debug(); visibility is controlled by VERBOSE_OUTPUT setting.
    """
    logging.debug(msg)
