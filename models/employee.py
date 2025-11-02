"""
Employee Model

Data model for employee information
"""

from dataclasses import dataclass, field
from typing import Optional

from .base import BaseModel


@dataclass
class Employee(BaseModel):
    """Employee data model"""
    
    employee_code: str = ""
    full_name: str = ""
    email: Optional[str] = None
    department_code: Optional[str] = None
    department_name: Optional[str] = None
    position: Optional[str] = None
    manager_code: Optional[str] = None
    
    def __post_init__(self):
        """Validate and normalize data after initialization"""
        # Call parent __post_init__ to set timestamps
        super().__post_init__()
        # Strip whitespace
        self.employee_code = self.employee_code.strip() if self.employee_code else ""
        self.full_name = self.full_name.strip() if self.full_name else ""
        
        if self.email:
            self.email = self.email.strip().lower()
        
        if self.department_code:
            self.department_code = self.department_code.strip().upper()
        
        if self.manager_code:
            self.manager_code = self.manager_code.strip()
    
    def __str__(self) -> str:
        return f"Employee({self.employee_code}: {self.full_name})"
    
    def __repr__(self) -> str:
        return self.__str__()
