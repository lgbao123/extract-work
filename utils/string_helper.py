"""
String Helper Module

Utility functions for string manipulation and parsing
"""

import re
from typing import Optional, Tuple
from .exceptions import ParsingError


def clean_string(text: Optional[str]) -> str:
    """
    Clean and normalize string
    
    Args:
        text: Input string
        
    Returns:
        Cleaned string
        
    Examples:
        >>> clean_string("  Hello  World  ")
        'Hello World'
        >>> clean_string(None)
        ''
    """
    if text is None or text.lower() == "nan":
        return ""
    
    # Convert to string
    text = str(text).strip()
    
    # Escape strings that look like numbers with dots (e.g., "2.2")
    # if re.compile(r'^\d+\.\d+$').match(text):
    #     return f"'" + text
    # # Remove multiple spaces
    # text = re.sub(r'\s+', ' ', text)
    
    # # Remove special characters that cause issues
    # text = text.replace('\x00', '')  # Null characters
    # text = text.replace('\r', '')    # Carriage returns
    
    return text


def normalize_code(code: Optional[str], uppercase: bool = True) -> str:
    """
    Normalize employee/department code
    
    Args:
        code: Code string
        uppercase: Convert to uppercase
        
    Returns:
        Normalized code
        
    Examples:
        >>> normalize_code("  nv001  ")
        'NV001'
        >>> normalize_code("it-dept", uppercase=False)
        'it-dept'
    """
    if code is None:
        return ""
    
    code = clean_string(code)
    
    if uppercase:
        code = code.upper()
    
    return code


def parse_stt(stt: str) -> Tuple[int, Optional[str]]:
    """
    Parse STT (số thứ tự) to get level and parent STT
    
    Args:
        stt: STT string (e.g., "1", "1.1", "1.1.1")
        
    Returns:
        Tuple of (level, parent_stt)
        
    Examples:
        >>> parse_stt("1")
        (0, None)
        >>> parse_stt("1.1")
        (1, "1")
        >>> parse_stt("1.1.1")
        (2, "1.1")
    """
    if not stt:
        return (0, None)
    
    stt = clean_string(stt)
    
    # Count dots to determine level
    level = stt.count('.')
    
    # Get parent STT
    if level == 0:
        parent_stt = None
    else:
        parts = stt.split('.')
        parent_stt = '.'.join(parts[:-1])
    
    return (level, parent_stt)


def parse_cost(cost_str: Optional[str]) -> float:
    """
    Parse cost string to float
    
    Args:
        cost_str: Cost string (can contain commas, currency symbols)
        
    Returns:
        Cost as float
        
    Raises:
        ParsingError: If cost cannot be parsed
        
    Examples:
        >>> parse_cost("1,000,000")
        1000000.0
        >>> parse_cost("1.500.000")
        1500000.0
        >>> parse_cost("$1,000")
        1000.0
    """
    if cost_str is None or cost_str == "" or cost_str.lower() == "nan":
        return 0.0
    
    # Convert to string and clean
    cost_str = str(cost_str).strip()
    
    if not cost_str:
        return 0.0
    
    # Remove currency symbols and whitespace
    cost_str = re.sub(r'[^\d.,\-]', '', cost_str)
    
    # Handle different decimal separators
    # Vietnamese format: 1.000.000,50 or 1,000,000.50
    
    # Count commas and dots
    comma_count = cost_str.count(',')
    dot_count = cost_str.count('.')
    
    if comma_count > 1 or dot_count > 1:
        # Multiple separators - assume thousand separators
        # Last one is decimal
        if cost_str.rfind(',') > cost_str.rfind('.'):
            # Comma is decimal separator
            cost_str = cost_str.replace('.', '').replace(',', '.')
        else:
            # Dot is decimal separator
            cost_str = cost_str.replace(',', '')
    elif comma_count == 1 and dot_count == 0:
        # Only comma - could be decimal or thousand
        parts = cost_str.split(',')
        if len(parts[1]) == 2:  # Likely decimal (e.g., 1000,50)
            cost_str = cost_str.replace(',', '.')
        else:  # Likely thousand separator
            cost_str = cost_str.replace(',', '')
    elif comma_count == 0 and dot_count == 1:
        # Only dot - keep as is (decimal separator in English format)
        pass
    
    # Remove any remaining thousand separators
    cost_str = cost_str.replace(',', '')
    
    # Convert to float
    try:
        return float(cost_str)
    except ValueError as e:
        raise ParsingError(f"Cannot parse cost: {cost_str}") from e


def truncate_string(text: Optional[str], max_length: int, suffix: str = "...") -> str:
    """
    Truncate string to maximum length
    
    Args:
        text: Input string
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated string
        
    Examples:
        >>> truncate_string("Hello World", 8)
        'Hello...'
        >>> truncate_string("Hi", 10)
        'Hi'
    """
    if text is None:
        return ""
    
    text = str(text)
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def extract_numbers(text: str) -> list:
    """
    Extract all numbers from text
    
    Args:
        text: Input string
        
    Returns:
        List of numbers as strings
        
    Examples:
        >>> extract_numbers("Report 2025-09 has 42 tasks")
        ['2025', '09', '42']
    """
    if not text:
        return []
    
    return re.findall(r'\d+', text)


def string_escaping(value: str) -> str:
    """
    Escape special characters in string for Google Sheets
        if string is "2.2"return "'2.2"
        if string cotains "-ABC -XYZ" return "'-ABC\n -XYZ"
    Args:
        value: Input string
    Returns:
        Escaped string
    """
    # if isinstance(value, str):
    #     if re.compile(r'^\d+\.\d+$').match(value):
    #         return f"' {value}"
    #     if '-' in value:
    #         return "'" + value.replace(' -', '\n -')
    # return value
    pass