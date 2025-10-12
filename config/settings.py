import os
from dotenv import load_dotenv

load_dotenv()

# MongoDB Configuration
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
DATABASE_NAME = os.getenv("DATABASE_NAME", "work_report_db")

# Collections
COLLECTION_EMPLOYEES = "employees"
COLLECTION_WORK_REPORTS = "work_reports"
COLLECTION_PROJECTS = "projects"
COLLECTION_TASK_TYPES = "task_types"

# Date Formats
DATE_FORMATS = [
    "%d/%m/%Y",
    "%d/%m/%y",
    "%Y-%m-%d",
    "%d-%m-%Y",
]

# Excel Configuration
EXCEL_SECTION_KEYWORDS = {
    "actual_functional": "CÔNG VIỆC THEO CHỨC NĂNG",
    "actual_project": "CÔNG VIỆC THAM GIA CÁC DỰ ÁN",
    "planned_functional": "KẾ HOẠCH CÔNG VIỆC",
}

# Default values
DEFAULT_REPORT_STATUS = "draft"
DEFAULT_COST_UNIT = "VND"