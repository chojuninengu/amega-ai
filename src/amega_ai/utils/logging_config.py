"""
Logging Configuration Module for Amega AI.

This module provides a centralized logging configuration with multiple handlers
and detailed formatting for different logging levels and components.
"""

import logging
import logging.handlers
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Union

# ANSI color codes for colored console output
COLORS = {
    'DEBUG': '\033[36m',    # Cyan
    'INFO': '\033[32m',     # Green
    'WARNING': '\033[33m',  # Yellow
    'ERROR': '\033[31m',    # Red
    'CRITICAL': '\033[41m', # Red background
    'RESET': '\033[0m'      # Reset color
}

class ColoredFormatter(logging.Formatter):
    """Custom formatter adding colors to log levels and structured information."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors and additional context."""
        # Add timestamp with milliseconds
        record.timestamp = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        
        # Add color to level name
        level_color = COLORS.get(record.levelname, COLORS['RESET'])
        record.colored_levelname = f"{level_color}{record.levelname}{COLORS['RESET']}"
        
        # Add process and thread information
        record.process_info = f"[Process:{record.process}|Thread:{record.thread}]"
        
        # Add component/module path
        record.component = record.module
        if record.funcName != '<module>':
            record.component = f"{record.module}.{record.funcName}"
        
        # Format the message
        message = super().format(record)
        
        # Add contextual information if available
        if hasattr(record, 'extra_context'):
            message += f"\nContext: {record.extra_context}"
            
        return message

def setup_logging(
    log_level: Union[str, int] = logging.INFO,
    log_file: Optional[str] = None,
    component_name: str = "amega_ai"
) -> logging.Logger:
    """
    Set up logging configuration with console and file handlers.
    
    Args:
        log_level: The logging level (default: INFO)
        log_file: Path to the log file (default: None)
        component_name: Name of the component being logged (default: "amega_ai")
    
    Returns:
        logging.Logger: Configured logger instance
    """
    # Create logs directory if it doesn't exist
    if log_file:
        log_dir = os.path.dirname(log_file)
        if log_dir:
            Path(log_dir).mkdir(parents=True, exist_ok=True)
    
    # Create logger
    logger = logging.getLogger(component_name)
    logger.setLevel(log_level)
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Console Handler with colored output
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_format = (
        "%(timestamp)s [%(colored_levelname)s] %(process_info)s "
        "%(component)s: %(message)s"
    )
    console_handler.setFormatter(ColoredFormatter(console_format))
    logger.addHandler(console_handler)
    
    # File Handler with detailed output
    if log_file:
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(log_level)
        file_format = (
            "%(asctime)s.%(msecs)03d [%(levelname)s] "
            "%(process_info)s %(component)s "
            "(%(pathname)s:%(lineno)d): "
            "%(message)s"
        )
        file_handler.setFormatter(logging.Formatter(file_format, datefmt='%Y-%m-%d %H:%M:%S'))
        logger.addHandler(file_handler)
    
    # Log startup information
    logger.info(f"Logging initialized for {component_name}")
    logger.info(f"Log level set to {logging.getLevelName(log_level)}")
    if log_file:
        logger.info(f"Log file: {os.path.abspath(log_file)}")
    
    return logger

def get_logger(
    component_name: str,
    extra_context: Optional[dict] = None
) -> logging.Logger:
    """
    Get a logger instance with optional context information.
    
    Args:
        component_name: Name of the component requesting the logger
        extra_context: Additional context to include in logs
    
    Returns:
        logging.Logger: Logger instance with context
    """
    logger = logging.getLogger(component_name)
    
    if extra_context:
        return logging.LoggerAdapter(logger, {'extra_context': extra_context})
    
    return logger 