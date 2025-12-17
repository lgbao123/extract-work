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
    
    def to_sheet_dict(self) -> dict:
        """Convert to dictionary for Google Sheets (camelCase columns)"""
        return {
            'departmentCode': self.department_code,
            'departmentName': self.department_name,
            'managerCode': self.manager_code or '',
            'parentDepartmentCode': self.parent_department_code or '',
            'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else '',
            'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else ''
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Department':
        """Create Department from dictionary (handles both camelCase and snake_case)"""
        # Convert camelCase keys to snake_case
        normalized = {
            'department_code': data.get('departmentCode') or data.get('department_code', ''),
            'department_name': data.get('departmentName') or data.get('department_name', ''),
            'manager_code': data.get('managerCode') or data.get('manager_code'),
            'parent_department_code': data.get('parentDepartmentCode') or data.get('parent_department_code'),
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
        return f"Department({self.department_code}: {self.department_name})"
    
    def __repr__(self) -> str:
        return self.__str__()
