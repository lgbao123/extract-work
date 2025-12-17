"""
Task Model

Data model for tasks (both actual and planned)
"""

from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime

from config.constants import TaskCategory, TaskType
from .base import BaseModel


@dataclass
class Task(BaseModel):
    """Base task data model"""
    
    task_id: str = ""
    report_code: str = ""
    stt: str = ""  # Số thứ tự (e.g., "1", "1.1", "1.1.1")
    task_name: str = ""
    task_type: Optional[str] = None
    category: TaskCategory = TaskCategory.FUNCTIONAL
    start_date: Optional[str] = None  # Format: YYYY-MM-DD
    end_date: Optional[str] = None    # Format: YYYY-MM-DD
    frequency: Optional[str] = None   # For recurring tasks (e.g., "Hằng ngày", "Hằng tuần")
    # description: Optional[str] = None
    # result: Optional[str] = None
    level: int = 0  # Hierarchy level (0, 1, 2, ...)
    parent_task_id: Optional[str] = None
    has_subtasks: bool = False
    subtask_count: int = 0
    
    def __post_init__(self):
        """Calculate level from stt and normalize data"""
        # Call parent __post_init__ to set timestamps
        super().__post_init__()
        
        # Calculate level from stt
        if self.stt:
            self.level = self.stt.count('.')
        
        # Normalize strings
        self.task_id = self.task_id.strip() if self.task_id else ""
        self.report_code = self.report_code.strip() if self.report_code else ""
        self.stt = self.stt.strip() if self.stt else ""
        self.task_name = self.task_name.strip() if self.task_name else ""
        
        # Ensure category is enum
        if isinstance(self.category, str):
            self.category = TaskCategory(self.category)
    
    def is_subtask(self) -> bool:
        """Check if this is a subtask (level > 0)"""
        return self.level > 0
    
    def get_parent_stt(self) -> Optional[str]:
        """
        Get parent STT from current STT
        
        Returns:
            Parent STT or None if root level
        """
        if self.level == 0:
            return None
        
        parts = self.stt.split('.')
        if len(parts) > 1:
            return '.'.join(parts[:-1])
        return None
    
    def to_sheet_dict(self) -> dict:
        """Convert to dictionary for spreadsheet (flat structure)"""
        return {
            'taskId': self.task_id,
            'reportCode': self.report_code,
            'stt': self.stt,
            'taskName': self.task_name,
            'taskType': self.task_type or '',
            'category': self.category.value if isinstance(self.category, TaskCategory) else self.category,
            'startDate': self.start_date or '',
            'endDate': self.end_date or '',
            'frequency': self.frequency or '',
            # 'description': self.description or '',
            # 'result': self.result or '',
            'level': self.level,
            'parentTaskId': self.parent_task_id or '',
            'hasSubtasks': self.has_subtasks,
            'subtaskCount': self.subtask_count,
            'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else ''
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Task':
        """Create Task from dictionary (handles both camelCase and snake_case)"""
        # Normalize keys
        normalized = {
            'task_id': data.get('taskId') or data.get('task_id', ''),
            'report_code': data.get('reportCode') or data.get('report_code', ''),
            'stt': str(data.get('stt', '')),  # Always convert to string
            'task_name': data.get('taskName') or data.get('task_name', ''),
            'task_type': data.get('taskType') or data.get('task_type'),
            'start_date': data.get('startDate') or data.get('start_date'),
            'end_date': data.get('endDate') or data.get('end_date'),
            'frequency': data.get('frequency'),
            # 'description': data.get('description'),
            # 'result': data.get('result'),
            'level': int(data.get('level', 0)) if data.get('level') else 0,
            'parent_task_id': data.get('parentTaskId') or data.get('parent_task_id'),
            'has_subtasks': bool(data.get('hasSubtasks') or data.get('has_subtasks', False)),
            'subtask_count': int(data.get('subtaskCount') or data.get('subtask_count', 0)),
        }
        
        # Handle category enum
        category_val = data.get('category')
        if category_val:
            if isinstance(category_val, TaskCategory):
                normalized['category'] = category_val
            elif isinstance(category_val, str):
                try:
                    normalized['category'] = TaskCategory(category_val)
                except ValueError:
                    normalized['category'] = TaskCategory.FUNCTIONAL
        else:
            normalized['category'] = TaskCategory.FUNCTIONAL
        
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
        return f"Task({self.stt}: {self.task_name})"


@dataclass
class ActualTask(Task):
    """Actual task with evaluation field"""
    
    results: Optional[str] = None
    challenges: Optional[str] = None
    evaluation: Optional[str] = None
    
    def to_sheet_dict(self) -> dict:
        """Convert to dictionary for Tasks_Actual sheet"""
        data = super().to_sheet_dict()
        data['results'] = self.results or ''
        data['challenges'] = self.challenges or ''
        data['evaluation'] = self.evaluation or ''
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ActualTask':
        """Create ActualTask from dictionary"""
        # Get base task fields using parent from_dict
        task = super().from_dict(data)
        
        # Add ActualTask specific field
        task_dict = task.__dict__.copy()
        task_dict['results'] = data.get('results')
        task_dict['challenges'] = data.get('challenges')
        task_dict['evaluation'] = data.get('evaluation')
        
        return cls(**task_dict)


@dataclass
class PlannedTask(Task):
    """Planned task with cost fields"""
    
    description: Optional[str] = None
    cost: float = 0.0
    cost_unit: str = "VND"
    
    def to_sheet_dict(self) -> dict:
        """Convert to dictionary for Tasks_Planned sheet"""
        data = super().to_sheet_dict()
        data['description'] = self.description or ''
        data['cost'] = self.cost
        data['costUnit'] = self.cost_unit
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'PlannedTask':
        """Create PlannedTask from dictionary"""
        # Get base task fields using parent from_dict
        task = super().from_dict(data)
        
        # Add PlannedTask specific fields
        task_dict = task.__dict__.copy()
        task_dict['description'] = data.get('description')
        task_dict['cost'] = float(data.get('cost', 0.0))
        task_dict['cost_unit'] = data.get('costUnit') or data.get('cost_unit', 'VND')
        
        return cls(**task_dict)
