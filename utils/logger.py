"""
Logging configuration for the customer support agent system.

This module sets up structured logging with different levels and outputs,
ensuring comprehensive logging throughout the application lifecycle.
"""

import os
import sys
from pathlib import Path
from loguru import logger


def setup_logging(log_level: str = "INFO", log_file: str = "logs/customer_support.log"):
    """
    Sets up the logging configuration for the application.

    This function configures loguru logger with:
    - Console output with color coding
    - File output with rotation
    - Structured formatting
    - Different log levels for different outputs

    Args:
        log_level (str): The minimum log level to capture
        log_file (str): Path to the log file
    """
    # Remove default logger
    logger.remove()

    # Create logs directory if it doesn't exist
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # Console logger with color
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>",
        level=log_level,
        colorize=True,
    )

    # File logger with rotation
    logger.add(
        log_file,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
        level=log_level,
        rotation="10 MB",
        retention="30 days",
        compression="zip",
    )

    # Error file logger for critical errors
    error_log_file = log_path.parent / "errors.log"
    logger.add(
        str(error_log_file),
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
        level="ERROR",
        rotation="5 MB",
        retention="90 days",
        compression="zip",
    )


def get_logger(name: str = None):
    """
    Returns a logger instance with the specified name.

    Args:
        name (str): The name for the logger (usually __name__)

    Returns:
        Logger: A configured logger instance
    """
    return logger.bind(name=name)


class LoggerMixin:
    """
    Mixin class that provides logging capabilities to other classes.

    This mixin automatically creates a logger instance for any class
    that inherits from it, using the class name as the logger name.
    """

    def __init__(self, *args, **kwargs):
        """Initialize the logger for this class."""
        super().__init__(*args, **kwargs)
        self.logger = get_logger(self.__class__.__name__)

    def log_info(self, message: str, **kwargs):
        """Log an info message."""
        self.logger.info(message, **kwargs)

    def log_warning(self, message: str, **kwargs):
        """Log a warning message."""
        self.logger.warning(message, **kwargs)

    def log_error(self, message: str, **kwargs):
        """Log an error message."""
        self.logger.error(message, **kwargs)

    def log_debug(self, message: str, **kwargs):
        """Log a debug message."""
        self.logger.debug(message, **kwargs)
