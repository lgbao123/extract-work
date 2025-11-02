"""
Data Transformers

Transform and clean parsed data
"""

import re
import pandas as pd
from typing import Any, Dict, List
from datetime import datetime

from utils import clean_string, parse_cost, get_logger

logger = get_logger(__name__)


class DataTransformer:
    """Transform and clean data"""
    
    @staticmethod
    def flatten_multiindex_columns(df: pd.DataFrame) -> pd.DataFrame:
        """
        Flatten multi-index column names
        
        Args:
            df: DataFrame with multi-index columns
            
        Returns:
            DataFrame with flattened column names
        """
        if isinstance(df.columns, pd.MultiIndex):
            # Join multi-level columns with underscore
            df.columns = [
                '_'.join(str(c).strip() for c in col if 'Unnamed' not in str(c))
                for col in df.columns.values
            ]
            
            # Clean up column names
            df.columns = [clean_string(col) for col in df.columns]
        
        return df
    
    @staticmethod
    def parse_cost(cost_str: str) -> float:
        """
        Parse cost string to float
        
        Handles formats like:
        - 1,000,000
        - 1.000.000
        - 1.000.000,50
        - 1,000,000.50
        
        Args:
            cost_str: Cost string
            
        Returns:
            Float value
        """
        return parse_cost(cost_str)
    
    @staticmethod
    def normalize_employee_code(code: str) -> str:
        """
        Normalize employee code format
        
        Args:
            code: Employee code
            
        Returns:
            Normalized code
        """
        code = clean_string(code).upper()
        
        # Remove any non-alphanumeric characters
        code = re.sub(r'[^A-Z0-9]', '', code)
        
        return code
    
    @staticmethod
    def normalize_department_code(code: str) -> str:
        """
        Normalize department code format
        
        Args:
            code: Department code
            
        Returns:
            Normalized code
        """
        code = clean_string(code).upper()
        
        # Remove any non-alphanumeric characters except dash/underscore
        code = re.sub(r'[^A-Z0-9\-_]', '', code)
        
        return code
    
    @staticmethod
    def clean_task_name(name: str) -> str:
        """
        Clean task name
        
        Args:
            name: Task name
            
        Returns:
            Cleaned name
        """
        name = clean_string(name)
        
        # Remove excessive whitespace
        name = re.sub(r'\s+', ' ', name)
        
        # Remove leading/trailing punctuation
        name = name.strip('.,;:!?')
        
        return name
    
    @staticmethod
    def parse_date_flexible(date_value: Any) -> datetime:
        """
        Parse date from various formats
        
        Args:
            date_value: Date value (str, datetime, or Excel serial)
            
        Returns:
            datetime object
        """
        from utils import parse_date
        
        if isinstance(date_value, datetime):
            return date_value
        
        if isinstance(date_value, (int, float)):
            # Excel serial date
            from datetime import timedelta
            return datetime(1899, 12, 30) + timedelta(days=date_value)
        
        return parse_date(str(date_value))
    
    @staticmethod
    def task_to_dict(task: Any) -> Dict[str, Any]:
        """
        Convert task object to dictionary for storage
        
        Args:
            task: Task object
            
        Returns:
            Dictionary
        """
        return task.to_sheet_dict()
    
    @staticmethod
    def tasks_to_dataframe(tasks: List[Any]) -> pd.DataFrame:
        """
        Convert list of tasks to DataFrame
        
        Args:
            tasks: List of task objects
            
        Returns:
            DataFrame
        """
        if not tasks:
            return pd.DataFrame()
        
        data = [task.to_sheet_dict() for task in tasks]
        df = pd.DataFrame(data)
        
        return df
    
    @staticmethod
    def deduplicate_tasks(tasks: List[Any]) -> List[Any]:
        """
        Remove duplicate tasks based on STT
        
        Args:
            tasks: List of tasks
            
        Returns:
            List of unique tasks
        """
        seen_stt = set()
        unique_tasks = []
        
        for task in tasks:
            if task.stt not in seen_stt:
                unique_tasks.append(task)
                seen_stt.add(task.stt)
            else:
                logger.warning(f"Duplicate task found: {task.stt}")
        
        return unique_tasks
    
    @staticmethod
    def sort_tasks_by_stt(tasks: List[Any]) -> List[Any]:
        """
        Sort tasks by STT in hierarchical order
        
        Args:
            tasks: List of tasks
            
        Returns:
            Sorted list of tasks
        """
        def stt_sort_key(task):
            # Convert "1.2.3" to (1, 2, 3) for proper sorting
            parts = str(task.stt).split('.')
            return tuple(int(p) for p in parts if p.isdigit())
        
        try:
            return sorted(tasks, key=stt_sort_key)
        except (ValueError, AttributeError):
            logger.warning("Could not sort tasks by STT, returning original order")
            return tasks
    
    @staticmethod
    def merge_task_updates(existing_task: Any, updated_task: Any) -> Any:
        """
        Merge updates into existing task
        
        Args:
            existing_task: Current task
            updated_task: Task with updates
            
        Returns:
            Merged task
        """
        # Create dict of non-None values from updated_task
        updates = {
            k: v for k, v in updated_task.to_dict().items()
            if v is not None and k not in ['task_id', 'created_at']
        }
        
        # Update existing task
        existing_dict = existing_task.to_dict()
        existing_dict.update(updates)
        
        # Create new task object
        task_class = type(existing_task)
        return task_class.from_dict(existing_dict)
