"""
Repositories Module

Data access layer for Google Sheets
"""

from .google_sheets_client import GoogleSheetsClient
from .base_repository import BaseRepository
from .employee_repository import EmployeeRepository
from .department_repository import DepartmentRepository
from .report_repository import ReportRepository
from .task_repository import TaskRepository
from .review_repository import ReviewRepository

__all__ = [
    'GoogleSheetsClient',
    'BaseRepository',
    'EmployeeRepository',
    'DepartmentRepository',
    'ReportRepository',
    'TaskRepository',
    'ReviewRepository'
]
