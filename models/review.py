"""
Review Model

Data model for report reviews/evaluations
"""

from dataclasses import dataclass
from typing import Optional

from .base import BaseModel


@dataclass
class Review(BaseModel):
    """Review/evaluation data model"""
    
    report_code: str = ""
    daily_work_review: Optional[str] = None
    professional_review: Optional[str] = None
    
    def __post_init__(self):
        """Normalize data"""
        # Call parent __post_init__ to set timestamps
        super().__post_init__()
        
        self.report_code = self.report_code.strip() if self.report_code else ""
    
    def to_sheet_dict(self) -> dict:
        """Convert to dictionary for Reviews sheet"""
        return {
            'reportCode': self.report_code,
            'dailyWorkReview': self.daily_work_review or '',
            'professionalReview': self.professional_review or '',
            'createdAt': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else ''
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Review':
        """Create Review from dictionary (handles both camelCase and snake_case)"""
        from datetime import datetime
        
        # Normalize keys
        normalized = {
            'report_code': data.get('reportCode') or data.get('report_code', ''),
            'daily_work_review': data.get('dailyWorkReview') or data.get('daily_work_review'),
            'professional_review': data.get('professionalReview') or data.get('professional_review'),
        }
        
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
        return f"Review({self.report_code})"
    
    def __repr__(self) -> str:
        return self.__str__()
