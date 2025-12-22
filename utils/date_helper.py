"""
Date Helper Module

Utility functions for date parsing and formatting
"""

from datetime import datetime
from typing import Optional, Dict
import re
import pandas as pd
import numpy as np
from config.constants import DATE_FORMATS
from .exceptions import ParsingError


def parse_date(date_value, formats: Optional[list] = None) -> Optional[datetime]:
    """
    Parse date from various formats
    
    Args:
        date_value: Date value (string, datetime, or other)
        formats: List of date format strings to try
        
    Returns:
        datetime object or None if parsing fails
        
    Examples:
        >>> parse_date("20/08/2025")
        datetime(2025, 8, 20, 0, 0)
        >>> parse_date("2025-08-20")
        datetime(2025, 8, 20, 0, 0)
    """
    if date_value is None or date_value == "":
        return None
    
    # Already a datetime
    if isinstance(date_value, datetime):
        return date_value
    
    # Convert to string
    date_str = str(date_value).strip()
    if not date_str:
        return None
    
    # Try each format
    formats_to_try = formats or DATE_FORMATS
    for fmt in formats_to_try:
        try:
            return datetime.strptime(date_str, fmt)
        except (ValueError, TypeError):
            continue
    
    # Failed to parse
    return None


def format_date(date_obj: Optional[datetime], format_str: str = "%Y-%m-%d") -> str:
    """
    Format datetime object to string
    
    Args:
        date_obj: datetime object
        format_str: Output format string
        
    Returns:
        Formatted date string or empty string
        
    Examples:
        >>> format_date(datetime(2025, 8, 20))
        '2025-08-20'
        >>> format_date(datetime(2025, 8, 20), "%d/%m/%Y")
        '20/08/2025'
    """
    if date_obj is None:
        return ""
    
    if isinstance(date_obj, str):
        date_obj = parse_date(date_obj)
        if date_obj is None:
            return ""
    
    try:
        return date_obj.strftime(format_str)
    except (AttributeError, ValueError):
        return ""


def extract_period_from_text(text: str) -> Dict[str, any]:
    """
    Extract report period from text
    
    Args:
        text: Text containing period information
            Example: "Từ ngày 20/08/2025 đến hết ngày 20/09/2025"
        
    Returns:
        Dictionary with year, month, start_date, end_date
        
    Raises:
        ParsingError: If period cannot be extracted
        
    Examples:
        >>> extract_period_from_text("Từ ngày 20/08/2025 đến hết ngày 20/09/2025")
        {'year': 2025, 'month': 9, 'start_date': '2025-08-20', 'end_date': '2025-09-20'}
    """
    if not text:
        raise ParsingError("Empty text provided")
    
    # Pattern: Từ ngày DD/MM/YYYY đến (hết ngày) DD/MM/YYYY
    pattern = r'[Tt]ừ\s+ngày\s+(\d{1,2})/(\d{1,2})/(\d{4})\s+đến\s+(?:hết\s+ngày\s+)?(\d{1,2})/(\d{1,2})/(\d{4})'
    match = re.search(pattern, text)
    
    if not match:
        raise ParsingError(f"Could not extract period from: {text}")
    
    start_day, start_month, start_year = match.groups()[:3]
    end_day, end_month, end_year = match.groups()[3:]
    
    # Convert to integers
    start_year = int(start_year)
    start_month = int(start_month)
    start_day = int(start_day)
    end_year = int(end_year)
    end_month = int(end_month)
    end_day = int(end_day)
    
    # Create datetime objects
    try:
        start_date = datetime(start_year, start_month, start_day)
        end_date = datetime(end_year, end_month, end_day)
    except ValueError as e:
        raise ParsingError(f"Invalid date in period: {e}")
    
    return {
        'year': start_year,
        'month': end_month,
        'start_date': format_date(start_date),
        'end_date': format_date(end_date)
    }


def get_month_range(year: int, month: int) -> Dict[str, str]:
    """
    Get start and end dates for a given month
    
    Args:
        year: Year
        month: Month (1-12)
        
    Returns:
        Dictionary with start_date and end_date
    """
    from calendar import monthrange
    
    last_day = monthrange(year, month)[1]
    
    start_date = datetime(year, month, 1)
    end_date = datetime(year, month, last_day)
    
    return {
        'start_date': format_date(start_date),
        'end_date': format_date(end_date)
    }
