"""
Base Parser

Abstract parser class for all file parsers
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
from pathlib import Path

from utils import ParsingError, get_logger

logger = get_logger(__name__)


class BaseParser(ABC):
    """Abstract base class for all parsers"""
    
    def __init__(self, file_path: Path):
        """
        Initialize parser
        
        Args:
            file_path: Path to file to parse
        """
        self.file_path = Path(file_path)
        self.validate_file()
    
    def validate_file(self) -> None:
        """
        Validate file exists and is readable
        
        Raises:
            ParsingError: If file is invalid
        """
        if not self.file_path.exists():
            raise ParsingError(f"File not found: {self.file_path}")
        
        if not self.file_path.is_file():
            raise ParsingError(f"Not a file: {self.file_path}")
        
        if not self.file_path.stat().st_size > 0:
            raise ParsingError(f"File is empty: {self.file_path}")
    
    @abstractmethod
    def parse(self) -> Dict[str, Any]:
        """
        Parse file and return structured data
        
        Returns:
            Dictionary with parsed data
            
        Raises:
            ParsingError: If parsing fails
        """
        pass
    
    @abstractmethod
    def extract_metadata(self) -> Dict[str, Any]:
        """
        Extract file metadata
        
        Returns:
            Dictionary with metadata
        """
        pass
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.file_path.name})"
