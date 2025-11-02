"""
Logger Module

Custom logger wrapper for the application
"""

import logging
from typing import Optional


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get a logger instance
    
    Args:
        name: Logger name (typically __name__ of the calling module)
        
    Returns:
        Logger instance
        
    Examples:
        >>> logger = get_logger(__name__)
        >>> logger.info("This is a log message")
    """
    if name:
        logger_name = f"work_report.{name}"
    else:
        logger_name = "work_report"
    
    return logging.getLogger(logger_name)
