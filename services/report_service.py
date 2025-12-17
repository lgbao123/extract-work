"""
Report Service

Orchestrates report import and processing
"""

from pathlib import Path
from typing import Dict, Any, Optional
import uuid
from datetime import datetime

from repositories import (
    GoogleSheetsClient,
    EmployeeRepository,
    DepartmentRepository,
    ReportRepository,
    TaskRepository,
    ReviewRepository
)
from parsers import ExcelParser, DataValidator
from models import WorkReport, Employee, Department, Review
from utils import ServiceError, get_logger
from utils.decorators import timing

logger = get_logger(__name__)


class ReportService:
    """Service for report operations"""
    
    def __init__(self, client: GoogleSheetsClient):
        """
        Initialize service
        
        Args:
            client: Google Sheets client
        """
        self.client = client
        self.employee_repo = EmployeeRepository(client)
        self.department_repo = DepartmentRepository(client)
        self.report_repo = ReportRepository(client)
        self.task_repo = TaskRepository(client)
        self.review_repo = ReviewRepository(client)
        self.validator = DataValidator()
    
    @timing
    def import_from_excel(self, file_path: str, 
                         employee_code: str,
                         department_code: str,
                         auto_update: bool = False) -> Dict[str, Any]:
        """
        Import work report from Excel file
        
        Args:
            file_path: Path to Excel file
            employee_code: Employee code
            department_code: Department code
            auto_update: Whether to update existing report
            
        Returns:
            Dictionary with import results
            
        Raises:
            ServiceError: If import fails
        """
        logger.info(f"Importing report from {file_path}")
        
        try:
            # Step 1: Parse Excel file
            parser = ExcelParser(Path(file_path))
            parsed_data = parser.parse()
            
            # # Step 2: Validate data
            # is_valid, errors = self.validator.validate_all(parsed_data)
            # if not is_valid:
            #     logger.error(f"Validation failed: {errors}")
            #     raise ServiceError(f"Validation failed: {errors}")
            
            # Step 3: Ensure employee exists
            employee = self._ensure_employee(employee_code, department_code)
            
            # Step 4: Generate report code
            period = parsed_data['metadata']['period']
            report_code = self._generate_report_code(
                employee_code,
                period.year,
                period.month
            )
            
            # Step 5: Check if report exists
            existing_report = self.report_repo.get_by_code(report_code)
            
            if existing_report and not auto_update:
                raise ServiceError(
                    f"Report {report_code} already exists. Use auto_update=True to replace."
                )
            
            # Step 6: Create or update report
            if existing_report:
                # Delete old tasks and reviews
                self.task_repo.delete_tasks_by_report(report_code, is_actual=True)
                self.task_repo.delete_tasks_by_report(report_code, is_actual=False)
                self.review_repo.delete(report_code)
                
                # Increment version
                version = existing_report.version + 1
                logger.info(f"Updating report {report_code} to version {version}")
            else:
                version = 1
                logger.info(f"Creating new report {report_code}")
            
            # Step 7: Create report record
            emp_name = parsed_data['metadata']['employee_name'] 
            report = WorkReport(
                report_code=report_code,
                employee_code=employee_code,
                employee_name=emp_name,
                department_code=department_code,
                period=period,
                status="submitted",
                version=version
            )
            
            if existing_report:
                self.report_repo.update(report_code, report.to_sheet_dict())
            else:
                self.report_repo.create(report)
            
            # Step 8: Create tasks
            task_counts = {}
            
            # Set report_code for all tasks
            for section in ['actual_functional_tasks', 'actual_project_tasks',
                           'planned_functional_tasks', 'planned_project_tasks']:
                tasks = parsed_data.get(section, [])
                for task in tasks:
                    task.report_code = report_code
            
            # Create actual tasks
            actual_functional = parsed_data.get('actual_functional_tasks', [])
            actual_project = parsed_data.get('actual_project_tasks', [])
            
            if actual_functional:
                self.task_repo.create_actual_tasks(actual_functional)
                task_counts['actual_functional'] = len(actual_functional)
            
            if actual_project:
                self.task_repo.create_actual_tasks(actual_project)
                task_counts['actual_project'] = len(actual_project)
            
            # Create planned tasks
            planned_functional = parsed_data.get('planned_functional_tasks', [])
            planned_project = parsed_data.get('planned_project_tasks', [])
            
            if planned_functional:
                self.task_repo.create_planned_tasks(planned_functional)
                task_counts['planned_functional'] = len(planned_functional)
            
            if planned_project:
                self.task_repo.create_planned_tasks(planned_project)
                task_counts['planned_project'] = len(planned_project)
            
            # Step 9: Create review
            reviews = parsed_data.get('reviews', {})
            review = Review(
                report_code=report_code,
                daily_work_review=reviews.get('daily_work', ''),
                professional_review=reviews.get('professional', '')
            )
            self.review_repo.create(review)
            
            # Step 10: Return results
            result = {
                'success': True,
                'report_code': report_code,
                'version': version,
                'employee_code': employee_code,
                'period': f"{period.year}-{period.month:02d}",
                'task_counts': task_counts,
                'total_tasks': sum(task_counts.values()),
                'action': 'updated' if existing_report else 'created'
            }
            
            logger.info(f"Successfully imported report: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to import report: {e}")
            raise ServiceError(f"Import failed: {e}") from e
    
    def _ensure_employee(self, employee_code: str, 
                        department_code: str) -> Employee:
        """Ensure employee exists, create if not"""
        employee = self.employee_repo.get_by_code(employee_code)
        
        if not employee:
            logger.info(f"Creating employee: {employee_code}")
            employee = Employee(
                employee_code=employee_code,
                full_name=f"Employee {employee_code}",
                email=f"{employee_code.lower()}@company.com",
                department_code=department_code
            )
            self.employee_repo.create(employee)
        
        return employee
    
    def _generate_report_code(self, employee_code: str, 
                             year: int, month: int) -> str:
        """Generate report code"""
        return f"RPT-{employee_code}-{year}{month:02d}"
    
    def get_report_summary(self, report_code: str) -> Optional[Dict[str, Any]]:
        """
        Get summary of a report
        
        Args:
            report_code: Report code
            
        Returns:
            Dictionary with report summary
        """
        try:
            report = self.report_repo.get_by_code(report_code)
            if not report:
                return None
            
            # Get tasks
            actual_functional = self.task_repo.get_actual_tasks_by_report(report_code)
            actual_project = self.task_repo.get_actual_tasks_by_report(report_code)
            planned_functional = self.task_repo.get_planned_tasks_by_report(report_code)
            planned_project = self.task_repo.get_planned_tasks_by_report(report_code)
            
            # Get review
            review = self.review_repo.get_by_report(report_code)
            
            return {
                'report': report.to_dict(),
                'task_counts': {
                    'actual_functional': len([t for t in actual_functional 
                                            if t.category.name == 'FUNCTIONAL']),
                    'actual_project': len([t for t in actual_project 
                                         if t.category.name == 'PROJECT']),
                    'planned_functional': len([t for t in planned_functional 
                                             if t.category.name == 'FUNCTIONAL']),
                    'planned_project': len([t for t in planned_project 
                                          if t.category.name == 'PROJECT']),
                },
                'has_review': review is not None
            }
            
        except Exception as e:
            logger.error(f"Failed to get report summary: {e}")
            return None
