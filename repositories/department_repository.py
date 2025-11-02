"""Department Repository"""

from typing import Dict, Any
from .base_repository import BaseRepository
from .google_sheets_client import GoogleSheetsClient
from models import Department
from config.constants import SheetName


class DepartmentRepository(BaseRepository[Department]):
    """Repository for Department data"""
    
    def __init__(self, client: GoogleSheetsClient):
        super().__init__(client, SheetName.DEPARTMENTS.value)
    
    def model_to_dict(self, model: Department) -> Dict[str, Any]:
        """Convert Department to dict"""
        return model.to_sheet_dict()
    
    def dict_to_model(self, data: Dict[str, Any]) -> Department:
        """Convert dict to Department"""
        return Department.from_dict(data)
    
    def get_id_column(self) -> str:
        """Get primary key column"""
        return "departmentCode"
    
    def get_by_code(self, department_code: str) -> Department:
        """Get department by code"""
        return self.get_by_id(department_code)
