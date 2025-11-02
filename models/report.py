"""
Report Model

Data model for work reports
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any

from config.constants import ReportStatus
from .base import BaseModel


@dataclass
class ReportPeriod:
    """Report period information"""
    
    year: int
    month: int
    start_date: str  # Format: YYYY-MM-DD
    end_date: str    # Format: YYYY-MM-DD
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'year': self.year,
            'month': self.month,
            'start_date': self.start_date,
            'end_date': self.end_date
        }


@dataclass
class WorkReport(BaseModel):
    """Work report data model"""
    
    report_code: str = ""
    employee_code: str = ""
    employee_name: str = ""
    department_code: Optional[str] = None
    report_period_year: Optional[int] = None
    report_period_month: Optional[int] = None
    report_period_start_date: Optional[str] = None
    report_period_end_date: Optional[str] = None
    status: ReportStatus = ReportStatus.DRAFT
    version: int = 1
    
    # Additional fields not stored in main report sheet
    period: Optional[ReportPeriod] = None
    actual_functional_tasks: List[Any] = field(default_factory=list)
    actual_project_tasks: List[Any] = field(default_factory=list)
    planned_functional_tasks: List[Any] = field(default_factory=list)
    planned_project_tasks: List[Any] = field(default_factory=list)
    reviews: Optional[Dict[str, str]] = None
    
    def __post_init__(self):
        """Initialize computed fields"""
        # Call parent __post_init__ to set timestamps
        super().__post_init__()
        
        # If period is provided, extract fields
        if self.period:
            self.report_period_year = self.period.year
            self.report_period_month = self.period.month
            self.report_period_start_date = self.period.start_date
            self.report_period_end_date = self.period.end_date
        # If flat fields are provided but period object is not, reconstruct it
        elif (self.report_period_year and self.report_period_month and 
              self.report_period_start_date and self.report_period_end_date):
            self.period = ReportPeriod(
                year=self.report_period_year,
                month=self.report_period_month,
                start_date=self.report_period_start_date,
                end_date=self.report_period_end_date
            )
        
        # Normalize codes
        self.report_code = self.report_code.strip() if self.report_code else ""
        self.employee_code = self.employee_code.strip() if self.employee_code else ""
        
        if self.department_code:
            self.department_code = self.department_code.strip().upper()
    
    def get_main_sheet_data(self) -> Dict[str, Any]:
        """
        Get data for Work_Reports sheet (without nested objects)
        
        Returns:
            Dictionary with flat structure for spreadsheet
        """
        return {
            'reportCode': self.report_code,
            'employeeCode': self.employee_code,
            'employeeName': self.employee_name,
            'departmentCode': self.department_code or '',
            'reportPeriodYear': self.report_period_year or '',
            'reportPeriodMonth': self.report_period_month or '',
            'reportPeriodStartDate': self.report_period_start_date or '',
            'reportPeriodEndDate': self.report_period_end_date or '',
            'status': self.status.value if isinstance(self.status, ReportStatus) else self.status,
            'version': self.version,
            'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else '',
            'updatedAt': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else ''
        }
    
    def __str__(self) -> str:
        return f"WorkReport({self.report_code}: {self.employee_name})"
    
    def __repr__(self) -> str:
        return self.__str__()
