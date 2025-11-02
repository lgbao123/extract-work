"""
Validation Service

Cross-entity validation
"""

from typing import Tuple, List, Dict, Any

from repositories import (
    EmployeeRepository,
    DepartmentRepository,
    ReportRepository
)
from models import WorkReport
from utils import ValidationError, get_logger

logger = get_logger(__name__)


class ValidationService:
    """Service for validation operations"""
    
    def __init__(self, employee_repo: EmployeeRepository,
                 department_repo: DepartmentRepository,
                 report_repo: ReportRepository):
        """
        Initialize service
        
        Args:
            employee_repo: Employee repository
            department_repo: Department repository
            report_repo: Report repository
        """
        self.employee_repo = employee_repo
        self.department_repo = department_repo
        self.report_repo = report_repo
    
    def validate_report_submission(self, employee_code: str,
                                   department_code: str,
                                   year: int, month: int) -> Tuple[bool, List[str]]:
        """
        Validate if employee can submit report
        
        Args:
            employee_code: Employee code
            department_code: Department code
            year: Report year
            month: Report month
            
        Returns:
            Tuple of (is_valid, list of error messages)
        """
        errors = []
        
        # Check employee exists
        employee = self.employee_repo.get_by_code(employee_code)
        if not employee:
            errors.append(f"Employee {employee_code} not found")
        elif employee.department_code != department_code:
            errors.append(
                f"Employee {employee_code} does not belong to department {department_code}"
            )
        
        # Check department exists
        department = self.department_repo.get_by_code(department_code)
        if not department:
            errors.append(f"Department {department_code} not found")
        
        # Check for duplicate report
        existing_reports = self.report_repo.get_by_employee_and_period(
            employee_code, year, month
        )
        if existing_reports:
            errors.append(
                f"Report already exists for {employee_code} in {year}-{month:02d} "
                f"(version {existing_reports[0].version})"
            )
        
        return len(errors) == 0, errors
    
    def validate_employee_department(self, employee_code: str,
                                    department_code: str) -> Tuple[bool, List[str]]:
        """
        Validate employee belongs to department
        
        Args:
            employee_code: Employee code
            department_code: Department code
            
        Returns:
            Tuple of (is_valid, list of error messages)
        """
        errors = []
        
        employee = self.employee_repo.get_by_code(employee_code)
        if not employee:
            errors.append(f"Employee {employee_code} not found")
            return False, errors
        
        if employee.department_code != department_code:
            errors.append(
                f"Employee {employee_code} belongs to {employee.department_code}, "
                f"not {department_code}"
            )
        
        return len(errors) == 0, errors
    
    def get_validation_report(self) -> Dict[str, Any]:
        """
        Generate validation report for all data
        
        Returns:
            Dictionary with validation results
        """
        issues = {
            'orphaned_employees': [],
            'empty_departments': [],
            'duplicate_reports': [],
            'invalid_periods': []
        }
        
        # Check for orphaned employees (department doesn't exist)
        all_employees = self.employee_repo.get_all()
        all_departments = {d.department_code for d in self.department_repo.get_all()}
        
        for employee in all_employees:
            if employee.department_code not in all_departments:
                issues['orphaned_employees'].append({
                    'employee_code': employee.employee_code,
                    'department_code': employee.department_code
                })
        
        # Check for empty departments (no employees)
        for dept_code in all_departments:
            employees = self.employee_repo.get_by_department(dept_code)
            if not employees:
                issues['empty_departments'].append(dept_code)
        
        # Check for duplicate reports
        all_reports = self.report_repo.get_all()
        report_keys = {}
        
        for report in all_reports:
            # Use flat fields instead of period object (which might not be loaded)
            year = report.report_period_year if hasattr(report, 'report_period_year') else None
            month = report.report_period_month if hasattr(report, 'report_period_month') else None
            
            if year is None or month is None:
                # Skip reports with invalid period data
                issues['invalid_periods'].append({
                    'report_code': report.report_code,
                    'employee_code': report.employee_code
                })
                continue
            
            key = (report.employee_code, year, month)
            if key in report_keys:
                issues['duplicate_reports'].append({
                    'employee_code': report.employee_code,
                    'period': f"{year}-{month:02d}",
                    'versions': [report_keys[key].version, report.version]
                })
            else:
                report_keys[key] = report
        
        # Summary
        summary = {
            'total_issues': sum(len(v) if isinstance(v, list) else 1 
                              for v in issues.values()),
            'orphaned_employees_count': len(issues['orphaned_employees']),
            'empty_departments_count': len(issues['empty_departments']),
            'duplicate_reports_count': len(issues['duplicate_reports']),
            'invalid_periods_count': len(issues['invalid_periods'])
        }
        
        return {
            'summary': summary,
            'issues': issues
        }
