"""
Constants Module

Define enums, sheet names, column mappings, and other constants
"""

from enum import Enum
from typing import Dict, List


class SheetName(str, Enum):
    """Google Sheets tab names"""
    EMPLOYEES = "Employees"
    DEPARTMENTS = "Departments"
    WORK_REPORTS = "Work_Reports"
    TASKS_ACTUAL = "Tasks_Actual"
    TASKS_PLANNED = "Tasks_Planned"
    REVIEWS = "Reviews"


class TaskCategory(str, Enum):
    """Task categories"""
    FUNCTIONAL = "functional"
    PROJECT = "project"


class TaskType(str, Enum):
    """Task types"""
    ACTUAL = "actual"
    PLANNED = "planned"


class ReportStatus(str, Enum):
    """Report status values"""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"


# Date formats for parsing
DATE_FORMATS: List[str] = [
    "%d/%m/%Y",
    "%d/%m/%y",
    "%Y-%m-%d",
    "%d-%m-%Y",
    "%Y/%m/%d",
]


# Excel section keywords for parsing
EXCEL_SECTION_KEYWORDS: Dict[str, str] = {
    "actual": "A. Thực hiện công việc tháng",
    "actual_functional": "CÔNG VIỆC THEO CHỨC NĂNG",
    "actual_project": "CÔNG VIỆC THAM GIA CÁC DỰ ÁN",
    "actual_review": "ĐÁNH GIÁ CHUNG",
    "planned": "B. Kế hoạch công việc tháng tiếp theo",
    "planned_functional": "CÔNG VIỆC THEO CHỨC NĂNG",
    "planned_project": "CÔNG VIỆC THAM GIA CÁC DỰ ÁN",
}


# Column mappings for Google Sheets
COLUMN_MAPPINGS: Dict[str, List[str]] = {
    SheetName.EMPLOYEES: [
        "employeeCode",
        "fullName",
        "email",
        "departmentCode",
        "departmentName",
        "position",
        "managerCode",
        "createdAt",
        "updatedAt"
    ],
    SheetName.DEPARTMENTS: [
        "departmentCode",
        "departmentName",
        "managerCode",
        "parentDepartmentCode",
        "createdAt",
        "updatedAt"
    ],
    SheetName.WORK_REPORTS: [
        "reportCode",
        "employeeCode",
        "employeeName",
        "departmentCode",
        "reportPeriodYear",
        "reportPeriodMonth",
        "reportPeriodStartDate",
        "reportPeriodEndDate",
        "status",
        "version",
        "createdAt",
        "updatedAt"
    ],
    SheetName.TASKS_ACTUAL: [
        "taskId",
        "reportCode",
        "stt",
        "taskName",
        "taskType",
        "category",
        "startDate",
        "endDate",
        "frequency",
        "description",
        "solution",
        "evaluation",
        "level",
        "parentTaskId",
        "hasSubtasks",
        "subtaskCount",
        "createdAt"
    ],
    SheetName.TASKS_PLANNED: [
        "taskId",
        "reportCode",
        "stt",
        "taskName",
        "taskType",
        "category",
        "startDate",
        "endDate",
        "frequency",
        "description",
        "solution",
        "cost",
        "costUnit",
        "level",
        "parentTaskId",
        "hasSubtasks",
        "subtaskCount",
        "createdAt"
    ],
    SheetName.REVIEWS: [
        "reportCode",
        "dailyWorkReview",
        "professionalReview",
        "createdAt"
    ]
}


# Default values
DEFAULT_COST_UNIT: str = "VND"
DEFAULT_REPORT_STATUS: ReportStatus = ReportStatus.DRAFT


# Validation rules
MAX_EMPLOYEE_CODE_LENGTH: int = 20
MAX_DEPARTMENT_CODE_LENGTH: int = 20
MAX_TASK_NAME_LENGTH: int = 500
MAX_DESCRIPTION_LENGTH: int = 5000


# API Rate Limiting
GOOGLE_API_QUOTA: Dict[str, int] = {
    "requests_per_100_seconds": 100,
    "requests_per_100_seconds_per_user": 100,
}
