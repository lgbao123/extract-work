"""
Base Model

Common base class for all data models
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any


@dataclass
class BaseModel:
    """Base model with common fields for all entities"""
    
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Set timestamps if not provided"""
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert model to dictionary
        
        Returns:
            Dictionary representation of the model
        """
        result = {}
        for key, value in self.__dict__.items():
            if isinstance(value, datetime):
                result[key] = value.strftime('%Y-%m-%d %H:%M:%S')
            elif isinstance(value, BaseModel):
                result[key] = value.to_dict()
            elif isinstance(value, list):
                result[key] = [
                    item.to_dict() if isinstance(item, BaseModel) else item
                    for item in value
                ]
            else:
                result[key] = value
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseModel':
        """
        Create model instance from dictionary
        
        Args:
            data: Dictionary with model data
            
        Returns:
            Model instance
        """
        # Filter out keys that don't exist in the dataclass
        valid_keys = {f.name for f in cls.__dataclass_fields__.values()}
        filtered_data = {k: v for k, v in data.items() if k in valid_keys}
        
        # Convert date strings to datetime objects
        for key in ['created_at', 'updated_at']:
            if key in filtered_data and isinstance(filtered_data[key], str):
                try:
                    filtered_data[key] = datetime.strptime(
                        filtered_data[key], 
                        '%Y-%m-%d %H:%M:%S'
                    )
                except (ValueError, TypeError):
                    filtered_data[key] = None
        
        return cls(**filtered_data)
    
    def update_timestamp(self) -> None:
        """Update the updated_at timestamp"""
        self.updated_at = datetime.now()
