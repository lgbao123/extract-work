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
    description: Optional[str] = None
    solution: Optional[str] = None
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
            'description': self.description or '',
            'solution': self.solution or '',
            'level': self.level,
            'parentTaskId': self.parent_task_id or '',
            'hasSubtasks': self.has_subtasks,
            'subtaskCount': self.subtask_count,
            'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else ''
        }
    
    def __str__(self) -> str:
        return f"Task({self.stt}: {self.task_name})"


@dataclass
class ActualTask(Task):
    """Actual task with evaluation field"""
    
    evaluation: Optional[str] = None
    
    def to_sheet_dict(self) -> dict:
        """Convert to dictionary for Tasks_Actual sheet"""
        data = super().to_sheet_dict()
        data['evaluation'] = self.evaluation or ''
        return data


@dataclass
class PlannedTask(Task):
    """Planned task with cost fields"""
    
    cost: float = 0.0
    cost_unit: str = "VND"
    
    def to_sheet_dict(self) -> dict:
        """Convert to dictionary for Tasks_Planned sheet"""
        data = super().to_sheet_dict()
        data['cost'] = self.cost
        data['costUnit'] = self.cost_unit
        return data
