"""Employee Repository"""

from typing import Dict, Any
from .base_repository import BaseRepository
from .google_sheets_client import GoogleSheetsClient
from models import Employee
from config.constants import SheetName


class EmployeeRepository(BaseRepository[Employee]):
    """Repository for Employee data"""
    
    def __init__(self, client: GoogleSheetsClient):
        super().__init__(client, SheetName.EMPLOYEES.value)
    
    def model_to_dict(self, model: Employee) -> Dict[str, Any]:
        """Convert Employee to dict"""
        return model.to_sheet_dict()
    
    def dict_to_model(self, data: Dict[str, Any]) -> Employee:
        """Convert dict to Employee"""
        return Employee.from_dict(data)
    
    def get_id_column(self) -> str:
        """Get primary key column"""
        return "employeeCode"
    
    def get_by_code(self, employee_code: str) -> Employee:
        """Get employee by code"""
        return self.get_by_id(employee_code)
    
    def get_by_department(self, department_code: str):
        """Get all employees in department"""
        return self.find_by("departmentCode", department_code)
