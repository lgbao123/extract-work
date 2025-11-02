"""
Department Model

Data model for department/organization information
"""

from dataclasses import dataclass
from typing import Optional

from .base import BaseModel


@dataclass
class Department(BaseModel):
    """Department data model"""
    
    department_code: str = ""
    department_name: str = ""
    manager_code: Optional[str] = None
    parent_department_code: Optional[str] = None
    
    def __post_init__(self):
        """Validate and normalize data after initialization"""
        # Call parent __post_init__ to set timestamps
        super().__post_init__()
        
        self.department_code = self.department_code.strip().upper() if self.department_code else ""
        self.department_name = self.department_name.strip() if self.department_name else ""
        
        if self.manager_code:
            self.manager_code = self.manager_code.strip()
        
        if self.parent_department_code:
            self.parent_department_code = self.parent_department_code.strip().upper()
    
    def __str__(self) -> str:
        return f"Department({self.department_code}: {self.department_name})"
    
    def __repr__(self) -> str:
        return self.__str__()
