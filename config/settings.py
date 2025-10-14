import os
from dotenv import load_dotenv

load_dotenv()

# Google Sheets Configuration
GOOGLE_SHEETS_CREDENTIALS_FILE = os.getenv("GOOGLE_SHEETS_CREDENTIALS_FILE", "credentials.json")
GOOGLE_SHEETS_SPREADSHEET_ID = os.getenv("GOOGLE_SHEETS_SPREADSHEET_ID", "")
GOOGLE_SHEETS_SPREADSHEET_NAME = os.getenv("GOOGLE_SHEETS_SPREADSHEET_NAME", "Work Report Database")

# Sheet Names (tabs in Google Sheets)
SHEET_EMPLOYEES = "Employees"
SHEET_WORK_REPORTS = "Work_Reports"
SHEET_TASKS_ACTUAL = "Tasks_Actual"
SHEET_TASKS_PLANNED = "Tasks_Planned"
SHEET_REVIEWS = "Reviews"

# Date Formats
DATE_FORMATS = [
    "%d/%m/%Y",
    "%d/%m/%y",
    "%Y-%m-%d",
    "%d-%m-%Y",
]

# Excel Configuration
EXCEL_SECTION_KEYWORDS = {
    "actual": "A. Thực hiện công việc tháng",
    "actual_functional": "CÔNG VIỆC THEO CHỨC NĂNG",
    "actual_project": "CÔNG VIỆC THAM GIA CÁC DỰ ÁN",
    "actual_review": "ĐÁNH GIÁ CHUNG",
    "planned": "B. Kế hoạch công việc tháng tiếp theo",
    "planned_functional": "CÔNG VIỆC THEO CHỨC NĂNG",
    "planned_project": "CÔNG VIỆC THAM GIA CÁC DỰ ÁN",
}

# Default values
DEFAULT_REPORT_STATUS = "draft"
DEFAULT_COST_UNIT = "VND"