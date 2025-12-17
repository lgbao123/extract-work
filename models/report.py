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
    
    def to_sheet_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Google Sheets (camelCase columns)"""
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
    
    def get_main_sheet_data(self) -> Dict[str, Any]:
        """Alias for to_sheet_dict() for backward compatibility"""
        return self.to_sheet_dict()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WorkReport':
        """Create WorkReport from dictionary (handles both camelCase and snake_case)"""
        from datetime import datetime
        
        # Normalize keys (support both naming conventions)
        normalized = {
            'report_code': data.get('reportCode') or data.get('report_code', ''),
            'employee_code': data.get('employeeCode') or data.get('employee_code', ''),
            'employee_name': data.get('employeeName') or data.get('employee_name', ''),
            'department_code': data.get('departmentCode') or data.get('department_code'),
            'report_period_year': data.get('reportPeriodYear') or data.get('report_period_year'),
            'report_period_month': data.get('reportPeriodMonth') or data.get('report_period_month'),
            'report_period_start_date': data.get('reportPeriodStartDate') or data.get('report_period_start_date'),
            'report_period_end_date': data.get('reportPeriodEndDate') or data.get('report_period_end_date'),
            'version': data.get('version', 1),
        }
        
        # Handle status enum
        status_val = data.get('status')
        if status_val:
            if isinstance(status_val, ReportStatus):
                normalized['status'] = status_val
            elif isinstance(status_val, str):
                try:
                    normalized['status'] = ReportStatus(status_val)
                except ValueError:
                    normalized['status'] = ReportStatus.DRAFT
        else:
            normalized['status'] = ReportStatus.DRAFT
        
        # Handle timestamps
        for key in ['created_at', 'updated_at']:
            camel_key = 'createdAt' if key == 'created_at' else 'updatedAt'
            value = data.get(camel_key) or data.get(key)
            if value and isinstance(value, str):
                try:
                    normalized[key] = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
                except (ValueError, TypeError):
                    normalized[key] = None
            else:
                normalized[key] = value
        
        return cls(**normalized)
    
    def __str__(self) -> str:
        return f"WorkReport({self.report_code}: {self.employee_name})"
    
    def __repr__(self) -> str:
        return self.__str__()
