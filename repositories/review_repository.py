"""Review Repository"""

from typing import Dict, Any
from .base_repository import BaseRepository
from .google_sheets_client import GoogleSheetsClient
from models import Review
from config.constants import SheetName


class ReviewRepository(BaseRepository[Review]):
    """Repository for Review data"""
    
    def __init__(self, client: GoogleSheetsClient):
        super().__init__(client, SheetName.REVIEWS.value)
    
    def model_to_dict(self, model: Review) -> Dict[str, Any]:
        """Convert Review to dict"""
        return model.to_sheet_dict()
    
    def dict_to_model(self, data: Dict[str, Any]) -> Review:
        """Convert dict to Review"""
        return Review.from_dict(data)
    
    def get_id_column(self) -> str:
        """Get primary key column"""
        return "reportCode"
    
    def get_by_report(self, report_code: str) -> Review:
        """Get review for a report"""
        return self.get_by_id(report_code)
