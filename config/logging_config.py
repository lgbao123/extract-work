"""
Logging Configuration Module

Setup and configure application logging
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

from .settings import Settings


def setup_logging(
    log_level: Optional[str] = None,
    log_file: Optional[Path] = None,
    console_output: bool = True
) -> logging.Logger:
    """
    Setup application logging
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (optional)
        console_output: Whether to output to console
        
    Returns:
        Configured logger instance
    """
    # Get log level
    level = log_level or Settings.LOG_LEVEL
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    
    # Create logger
    logger = logging.getLogger('work_report')
    logger.setLevel(numeric_level)
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(numeric_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # File handler
    if log_file is None:
        # Default log file with timestamp
        Settings.ensure_directories()
        timestamp = datetime.now().strftime('%Y%m%d')
        log_file = Settings.LOGS_DIR / f'work_report_{timestamp}.log'
    
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(numeric_level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    logger.info(f"Logging initialized - Level: {level}")
    logger.info(f"Log file: {log_file}")
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(f'work_report.{name}')


# Create default logger
default_logger = setup_logging()
