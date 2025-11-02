"""
Data Validators

Validate parsed data before processing
"""

from typing import Dict, List, Any, Tuple
from datetime import datetime

from models import ActualTask, PlannedTask, WorkReport, Employee, Department
from utils import ValidationError, get_logger

logger = get_logger(__name__)


class DataValidator:
    """Validate parsed data"""
    
    @staticmethod
    def validate_employee(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate employee data
        
        Args:
            data: Employee data dictionary
            
        Returns:
            Tuple of (is_valid, list of error messages)
        """
        errors = []
        
        # Required fields
        if not data.get('employee_code'):
            errors.append("employee_code is required")
        
        if not data.get('name'):
            errors.append("name is required")
        
        if not data.get('department_code'):
            errors.append("department_code is required")
        
        # Email format
        email = data.get('email')
        if email and '@' not in email:
            errors.append(f"Invalid email format: {email}")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_department(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate department data"""
        errors = []
        
        if not data.get('department_code'):
            errors.append("department_code is required")
        
        if not data.get('name'):
            errors.append("name is required")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_report(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate work report metadata from Excel parser.
        Only validates data that comes from Excel, not generated fields like report_code or employee_code.
        
        Args:
            data: Dictionary with 'period' key containing ReportPeriod object
            
        Returns:
            Tuple of (is_valid, list of error messages)
        """
        errors = []
        
        # Validate period (the only required field from Excel)
        period = data.get('period')
        if not period:
            errors.append("period is required")
            return False, errors  # Can't validate further without period
        
        # Check period has required fields (strings from Excel)
        if not hasattr(period, 'year') or not period.year:
            errors.append("period.year is required")
        
        if not hasattr(period, 'month') or not period.month:
            errors.append("period.month is required")
            
        if not hasattr(period, 'start_date') or not period.start_date:
            errors.append("period.start_date is required")
        elif not isinstance(period.start_date, str):
            errors.append("period.start_date must be a string in YYYY-MM-DD format")
        
        if not hasattr(period, 'end_date') or not period.end_date:
            errors.append("period.end_date is required")
        elif not isinstance(period.end_date, str):
            errors.append("period.end_date must be a string in YYYY-MM-DD format")
        
        # Validate date ordering (both must exist as strings)
        if (hasattr(period, 'start_date') and hasattr(period, 'end_date') and 
            period.start_date and period.end_date and
            isinstance(period.start_date, str) and isinstance(period.end_date, str)):
            if period.start_date >= period.end_date:
                errors.append(f"start_date ({period.start_date}) must be before end_date ({period.end_date})")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_task(task: Any, task_type: str) -> Tuple[bool, List[str]]:
        """
        Validate task data
        
        Args:
            task: ActualTask or PlannedTask object
            task_type: 'actual' or 'planned'
            
        Returns:
            Tuple of (is_valid, list of error messages)
        """
        errors = []
        
        # Required fields
        if not task.stt:
            errors.append("STT is required")
        
        if not task.task_name:
            errors.append("task_name is required")
        
        # STT format (must be numeric with dots)
        stt = str(task.stt)
        if not all(c.isdigit() or c == '.' for c in stt):
            errors.append(f"Invalid STT format: {stt}")
        
        # Date validation
        if task.start_date and task.end_date:
            try:
                start = datetime.strptime(task.start_date, '%Y-%m-%d')
                end = datetime.strptime(task.end_date, '%Y-%m-%d')
                
                if start > end:
                    errors.append(f"start_date ({task.start_date}) must be before end_date ({task.end_date})")
            except ValueError as e:
                errors.append(f"Invalid date format: {e}")
        
        # Type-specific validation
        if task_type == 'planned':
            if hasattr(task, 'cost') and task.cost < 0:
                errors.append(f"cost cannot be negative: {task.cost}")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_task_hierarchy(tasks: List[Any]) -> Tuple[bool, List[str]]:
        """
        Validate task hierarchy is correct
        
        Args:
            tasks: List of tasks
            
        Returns:
            Tuple of (is_valid, list of error messages)
        """
        errors = []
        
        if not tasks:
            return True, []
        
        # Create STT to task mapping
        stt_map = {task.stt: task for task in tasks}
        
        # Validate each task's parent exists
        for task in tasks:
            if task.parent_task_id:
                # Find parent by parent_task_id
                parent_found = any(t.task_id == task.parent_task_id for t in tasks)
                
                if not parent_found:
                    errors.append(
                        f"Task {task.stt} references non-existent parent: {task.parent_task_id}"
                    )
            
            # Validate level matches STT
            stt_parts = str(task.stt).split('.')
            expected_level = len(stt_parts) - 1
            
            if task.level != expected_level:
                errors.append(
                    f"Task {task.stt} has incorrect level: {task.level} "
                    f"(expected {expected_level})"
                )
        
        # Validate no circular references
        for task in tasks:
            visited = set()
            current = task
            
            while current.parent_task_id:
                if current.task_id in visited:
                    errors.append(f"Circular reference detected for task {task.stt}")
                    break
                
                visited.add(current.task_id)
                
                # Find parent
                parent = next(
                    (t for t in tasks if t.task_id == current.parent_task_id),
                    None
                )
                
                if not parent:
                    break
                
                current = parent
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_all(report_data: Dict[str, Any]) -> Tuple[bool, Dict[str, List[str]]]:
        """
        Validate all report data
        
        Args:
            report_data: Complete report data
            
        Returns:
            Tuple of (is_valid, dictionary of errors by section)
        """
        all_errors = {}
        
        # Validate metadata
        if 'metadata' in report_data:
            _, errors = DataValidator.validate_report(report_data['metadata'])
            if errors:
                all_errors['metadata'] = errors
        
        # Validate tasks
        task_sections = [
            'actual_functional_tasks',
            'actual_project_tasks',
            'planned_functional_tasks',
            'planned_project_tasks'
        ]
        
        for section in task_sections:
            if section not in report_data:
                continue
            
            tasks = report_data[section]
            task_type = 'actual' if 'actual' in section else 'planned'
            
            section_errors = []
            
            # Validate each task
            for task in tasks:
                is_valid, errors = DataValidator.validate_task(task, task_type)
                if not is_valid:
                    section_errors.extend([f"Task {task.stt}: {e}" for e in errors])
            
            # Validate hierarchy
            is_valid, errors = DataValidator.validate_task_hierarchy(tasks)
            if not is_valid:
                section_errors.extend(errors)
            
            if section_errors:
                all_errors[section] = section_errors
        
        is_valid = len(all_errors) == 0
        
        if not is_valid:
            logger.warning(f"Validation failed with {len(all_errors)} sections having errors")
        
        return is_valid, all_errors
