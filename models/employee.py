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
    
    def to_sheet_dict(self) -> dict:
        """Convert to dictionary for Google Sheets (camelCase columns)"""
        return {
            'employeeCode': self.employee_code,
            'fullName': self.full_name,
            'email': self.email or '',
            'departmentCode': self.department_code or '',
            'departmentName': self.department_name or '',
            'position': self.position or '',
            'managerCode': self.manager_code or '',
            'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else '',
            'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else ''
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Employee':
        """Create Employee from dictionary (handles both camelCase and snake_case)"""
        # Convert camelCase keys to snake_case
        normalized = {
            'employee_code': data.get('employeeCode') or data.get('employee_code', ''),
            'full_name': data.get('fullName') or data.get('full_name', ''),
            'email': data.get('email'),
            'department_code': data.get('departmentCode') or data.get('department_code'),
            'department_name': data.get('departmentName') or data.get('department_name'),
            'position': data.get('position'),
            'manager_code': data.get('managerCode') or data.get('manager_code'),
        }
        
        # Handle timestamps
        for key in ['created_at', 'updated_at']:
            camel_key = 'createdAt' if key == 'created_at' else 'updatedAt'
            value = data.get(camel_key) or data.get(key)
            if value and isinstance(value, str):
                from datetime import datetime
                try:
                    normalized[key] = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
                except (ValueError, TypeError):
                    normalized[key] = None
            else:
                normalized[key] = value
        
        return cls(**normalized)
    
    def __str__(self) -> str:
        return f"Employee({self.employee_code}: {self.full_name})"
    
    def __repr__(self) -> str:
        return self.__str__()
