"""
Task Service

Business logic for task operations
"""

from typing import List, Dict, Any
from collections import defaultdict

from repositories import TaskRepository
from models import ActualTask, PlannedTask
from config.constants import TaskCategory
from utils import get_logger

logger = get_logger(__name__)


class TaskService:
    """Service for task operations"""
    
    def __init__(self, task_repo: TaskRepository):
        """
        Initialize service
        
        Args:
            task_repo: Task repository
        """
        self.task_repo = task_repo
    
    def get_task_hierarchy(self, report_code: str, 
                          is_actual: bool = True,
                          category: TaskCategory = None) -> List[Dict[str, Any]]:
        """
        Get tasks in hierarchical structure
        
        Args:
            report_code: Report code
            is_actual: Whether to get actual or planned tasks
            category: Filter by category
            
        Returns:
            List of tasks with nested subtasks
        """
        # Get tasks
        if is_actual:
            if category:
                tasks = self.task_repo.get_actual_tasks_by_category(report_code, category)
            else:
                tasks = self.task_repo.get_actual_tasks_by_report(report_code)
        else:
            if category:
                tasks = self.task_repo.get_planned_tasks_by_category(report_code, category)
            else:
                tasks = self.task_repo.get_planned_tasks_by_report(report_code)
        
        # Build hierarchy
        return self._build_hierarchy(tasks)
    
    def _build_hierarchy(self, tasks: List) -> List[Dict[str, Any]]:
        """Build hierarchical structure from flat task list"""
        # Create task map
        task_map = {task.task_id: task for task in tasks}
        
        # Group by parent
        children_map = defaultdict(list)
        root_tasks = []
        
        for task in tasks:
            if task.parent_task_id and task.parent_task_id in task_map:
                children_map[task.parent_task_id].append(task)
            else:
                root_tasks.append(task)
        
        # Build tree recursively
        def build_tree(task):
            task_dict = task.to_dict()
            subtasks = children_map.get(task.task_id, [])
            
            if subtasks:
                task_dict['subtasks'] = [build_tree(st) for st in subtasks]
            
            return task_dict
        
        return [build_tree(task) for task in root_tasks]
    
    def calculate_task_statistics(self, report_code: str) -> Dict[str, Any]:
        """
        Calculate task statistics for a report
        
        Args:
            report_code: Report code
            
        Returns:
            Dictionary with statistics
        """
        # Get all tasks
        actual_functional = self.task_repo.get_actual_tasks_by_category(
            report_code, TaskCategory.FUNCTIONAL
        )
        actual_project = self.task_repo.get_actual_tasks_by_category(
            report_code, TaskCategory.PROJECT
        )
        planned_functional = self.task_repo.get_planned_tasks_by_category(
            report_code, TaskCategory.FUNCTIONAL
        )
        planned_project = self.task_repo.get_planned_tasks_by_category(
            report_code, TaskCategory.PROJECT
        )
        
        # Calculate statistics
        stats = {
            'total_actual': len(actual_functional) + len(actual_project),
            'total_planned': len(planned_functional) + len(planned_project),
            'actual_functional': len(actual_functional),
            'actual_project': len(actual_project),
            'planned_functional': len(planned_functional),
            'planned_project': len(planned_project),
            'actual_by_level': self._count_by_level(actual_functional + actual_project),
            'planned_by_level': self._count_by_level(planned_functional + planned_project),
        }
        
        # Calculate planned costs
        total_cost = sum(t.cost or 0 for t in planned_functional + planned_project)
        stats['planned_total_cost'] = total_cost
        stats['planned_functional_cost'] = sum(t.cost or 0 for t in planned_functional)
        stats['planned_project_cost'] = sum(t.cost or 0 for t in planned_project)
        
        return stats
    
    def _count_by_level(self, tasks: List) -> Dict[int, int]:
        """Count tasks by hierarchy level"""
        level_counts = defaultdict(int)
        for task in tasks:
            level_counts[task.level] += 1
        return dict(level_counts)
