"""Task Repository"""

from typing import Dict, Any, List
from .base_repository import BaseRepository
from .google_sheets_client import GoogleSheetsClient
from models import ActualTask, PlannedTask
from config.constants import SheetName, TaskCategory
from utils import get_logger

logger = get_logger(__name__)


class TaskRepository(BaseRepository):
    """Repository for Task data (both actual and planned)"""
    
    def __init__(self, client: GoogleSheetsClient):
        # Initialize with None, will be set per operation
        super().__init__(client, SheetName.TASKS_ACTUAL.value)
    
    def model_to_dict(self, model) -> Dict[str, Any]:
        """Convert Task to dict"""
        return model.to_sheet_dict()
    
    def dict_to_model(self, data: Dict[str, Any]):
        """Convert dict to Task - must be overridden per task type"""
        # This will be called by specific methods
        return data
    
    def get_id_column(self) -> str:
        """Get primary key column"""
        return "taskId"
    
    # Actual Tasks methods
    
    def create_actual_task(self, task: ActualTask) -> ActualTask:
        """Create actual task"""
        self.sheet_name = SheetName.TASKS_ACTUAL.value
        return self.create(task)
    
    def create_actual_tasks(self, tasks: List[ActualTask]) -> List[ActualTask]:
        """Create multiple actual tasks"""
        self.sheet_name = SheetName.TASKS_ACTUAL.value
        return self.create_many(tasks)
    
    def get_actual_tasks_by_report(self, report_code: str) -> List[ActualTask]:
        """Get all actual tasks for a report"""
        self.sheet_name = SheetName.TASKS_ACTUAL.value
        rows = self.find_by("reportCode", report_code)
        return [ActualTask.from_dict(row if isinstance(row, dict) else row.to_dict()) 
                for row in rows]
    
    def get_actual_tasks_by_category(self, report_code: str, 
                                    category: TaskCategory) -> List[ActualTask]:
        """Get actual tasks by category"""
        all_tasks = self.get_actual_tasks_by_report(report_code)
        return [t for t in all_tasks if t.category == category]
    
    # Planned Tasks methods
    
    def create_planned_task(self, task: PlannedTask) -> PlannedTask:
        """Create planned task"""
        self.sheet_name = SheetName.TASKS_PLANNED.value
        return self.create(task)
    
    def create_planned_tasks(self, tasks: List[PlannedTask]) -> List[PlannedTask]:
        """Create multiple planned tasks"""
        self.sheet_name = SheetName.TASKS_PLANNED.value
        return self.create_many(tasks)
    
    def get_planned_tasks_by_report(self, report_code: str) -> List[PlannedTask]:
        """Get all planned tasks for a report"""
        self.sheet_name = SheetName.TASKS_PLANNED.value
        rows = self.find_by("reportCode", report_code)
        return [PlannedTask.from_dict(row if isinstance(row, dict) else row.to_dict()) 
                for row in rows]
    
    def get_planned_tasks_by_category(self, report_code: str, 
                                     category: TaskCategory) -> List[PlannedTask]:
        """Get planned tasks by category"""
        all_tasks = self.get_planned_tasks_by_report(report_code)
        return [t for t in all_tasks if t.category == category]
    
    # Common methods
    
    def delete_tasks_by_report(self, report_code: str, is_actual: bool = True) -> int:
        """Delete all tasks for a report"""
        sheet_name = (SheetName.TASKS_ACTUAL.value if is_actual 
                     else SheetName.TASKS_PLANNED.value)
        self.sheet_name = sheet_name
        
        count = self.client.delete_rows(sheet_name, "reportCode", report_code)
        logger.info(f"Deleted {count} {'actual' if is_actual else 'planned'} tasks for {report_code}")
        return count
