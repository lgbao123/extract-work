"""Report Repository"""

from typing import Dict, Any, List
from .base_repository import BaseRepository
from .google_sheets_client import GoogleSheetsClient
from models import WorkReport
from config.constants import SheetName
from utils import get_logger

logger = get_logger(__name__)


class ReportRepository(BaseRepository[WorkReport]):
    """Repository for WorkReport data"""
    
    def __init__(self, client: GoogleSheetsClient):
        super().__init__(client, SheetName.WORK_REPORTS.value)
    
    def model_to_dict(self, model: WorkReport) -> Dict[str, Any]:
        """Convert WorkReport to dict"""
        return model.to_sheet_dict()
    
    def dict_to_model(self, data: Dict[str, Any]) -> WorkReport:
        """Convert dict to WorkReport"""
        return WorkReport.from_dict(data)
    
    def get_id_column(self) -> str:
        """Get primary key column"""
        return "reportCode"
    
    def get_by_code(self, report_code: str) -> WorkReport:
        """Get report by code"""
        return self.get_by_id(report_code)
    
    def get_by_employee(self, employee_code: str) -> List[WorkReport]:
        """Get all reports for an employee"""
        return self.find_by("employeeCode", employee_code)
    
    def get_by_employee_and_period(self, employee_code: str, 
                                   year: int, month: int) -> List[WorkReport]:
        """Get reports for employee in specific period"""
        all_reports = self.get_by_employee(employee_code)
        
        # Filter by year and month
        filtered = [
            r for r in all_reports
            if r.period.year == year and r.period.month == month
        ]
        
        return filtered
    
    def get_latest_version(self, employee_code: str, 
                          year: int, month: int) -> WorkReport:
        """Get latest version of report for employee and period"""
        reports = self.get_by_employee_and_period(employee_code, year, month)
        
        if not reports:
            return None
        
        # Sort by version descending
        reports.sort(key=lambda r: r.version, reverse=True)
        return reports[0]
