# 🚀 Quick Start Guide - New Architecture

## Prerequisites

1. **Python 3.8+** installed
2. **Google Service Account** credentials (JSON file)
3. **Google Spreadsheet** created and shared with service account

---

## Setup (First Time)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
Create `.env` file in project root:
```env
GOOGLE_SHEETS_CREDENTIALS_FILE=credentials.json
GOOGLE_SHEETS_SPREADSHEET_ID=your_actual_spreadsheet_id
GOOGLE_SHEETS_SPREADSHEET_NAME=Work Report Database
DEBUG=False
LOG_LEVEL=INFO
```

### 3. Place Credentials
- Download `credentials.json` from Google Cloud Console
- Place in project root directory
- Share your Google Spreadsheet with the service account email

---

## Usage

### Import a Single Report
```bash
python main.py import \
  --file "input/202509_Bao cao cong viec_thinhdv.xlsx" \
  --employee "NV001" \
  --department "IT"
```

**What happens:**
1. ✅ Connects to Google Sheets
2. ✅ Parses Excel file (sections, tasks, reviews)
3. ✅ Validates all data
4. ✅ Creates employee if not exists
5. ✅ Inserts work report
6. ✅ Inserts actual/planned tasks with hierarchy
7. ✅ Inserts reviews
8. ✅ Shows summary

**Output:**
```
✓ Connected to Google Sheets

📄 Processing file: input/report.xlsx
✓ Success: created report RPT-NV001-202409
  → Period: 2024-09
  → Total tasks: 45
  → Task breakdown:
    - actual_functional: 12
    - actual_project: 8
    - planned_functional: 15
    - planned_project: 10

✓ Complete
```

---

### Import with Auto-Update
If report already exists, use `--auto-update` to replace it:
```bash
python main.py import \
  --file "input/report.xlsx" \
  --employee "NV001" \
  --department "IT" \
  --auto-update
```

**What happens:**
1. ✅ Checks if report exists
2. ✅ Deletes old tasks and reviews
3. ✅ Increments version number
4. ✅ Re-imports everything fresh

---

### Import Multiple Reports (Batch)
```bash
python main.py batch \
  --files "input/report1.xlsx" "input/report2.xlsx" "input/report3.xlsx" \
  --employees "NV001" "NV002" "NV003" \
  --departments "IT" "HR" "Sales"
```

**Output:**
```
🚀 Starting batch import of 3 reports...

📄 Processing file: input/report1.xlsx
✓ Success: created report RPT-NV001-202409

📄 Processing file: input/report2.xlsx
✓ Success: created report RPT-NV002-202409

📄 Processing file: input/report3.xlsx
✓ Success: created report RPT-NV003-202409

📊 Results: ✓ 3 successful, ✗ 0 failed
```

---

### View Report Summary
```bash
python main.py view --report "RPT-NV001-202409"
```

**Output:**
```
📋 Report Summary: RPT-NV001-202409

Employee: Nguyen Van A (NV001)
Period: 2024-09
Status: submitted
Version: 1

Task Counts:
  Actual Functional: 12
  Actual Project: 8
  Planned Functional: 15
  Planned Project: 10
  Has Review: Yes
```

---

### Run Validation
Check data integrity across all sheets:
```bash
python main.py validate
```

**Output:**
```
🔍 Running validation checks...

📊 Validation Summary:
  Total Issues: 2
  Orphaned Employees: 1
  Empty Departments: 0
  Duplicate Reports: 1

⚠️  Issues Found:
  - Employee NV999 references non-existent department XYZ
  - Duplicate report for NV001 in 2024-09
```

---

## Understanding the Code

### Flow: Import Report

```python
# 1. Setup
settings = Settings()                    # Load from .env
client = GoogleSheetsClient(settings)    # Connect to Sheets
report_service = ReportService(client)   # Initialize service

# 2. Import
result = report_service.import_from_excel(
    file_path="input/report.xlsx",
    employee_code="NV001",
    department_code="IT",
    auto_update=False
)

# 3. Behind the scenes:
# a) ExcelParser.parse() → Extract sections, tasks, reviews
# b) DataValidator.validate_all() → Validate data
# c) EmployeeRepository.create() → Ensure employee exists
# d) ReportRepository.create() → Create work report
# e) TaskRepository.create_actual_tasks() → Insert tasks
# f) ReviewRepository.create() → Insert reviews
```

### Key Classes

**Models** (Data Structures):
- `Employee`: Employee information
- `Department`: Department information
- `WorkReport`: Work report metadata
- `ActualTask` / `PlannedTask`: Task data with hierarchy
- `Review`: Performance reviews

**Parsers** (Data Extraction):
- `ExcelParser`: Parse Excel files
- `DataValidator`: Validate parsed data
- `DataTransformer`: Clean and transform data

**Repositories** (Data Access):
- `GoogleSheetsClient`: API wrapper
- `EmployeeRepository`: Employee CRUD
- `ReportRepository`: Report CRUD
- `TaskRepository`: Task CRUD
- `ReviewRepository`: Review CRUD

**Services** (Business Logic):
- `ReportService`: Orchestrate import process
- `TaskService`: Task hierarchy and statistics
- `ValidationService`: Data integrity checks

---

## Troubleshooting

### Error: "Credentials file not found"
```bash
# Solution: Check .env file
cat .env  # Should show GOOGLE_SHEETS_CREDENTIALS_FILE=credentials.json

# Verify credentials.json exists
ls -la credentials.json
```

### Error: "Sheet not found"
```bash
# Solution: Check spreadsheet ID
# Open your Google Spreadsheet
# URL: https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit
# Copy SPREADSHEET_ID and update .env
```

### Error: "Permission denied"
```bash
# Solution: Share spreadsheet with service account
# 1. Open credentials.json
# 2. Find "client_email": "xxx@xxx.iam.gserviceaccount.com"
# 3. In Google Sheets, click Share
# 4. Add service account email with Editor permissions
```

### Error: "Validation failed"
```bash
# Solution: Check your Excel file structure
# Required sections:
# - "1. Công việc theo chức năng" (Actual Functional)
# - "2. Công việc theo dự án" (Actual Project)  
# - "II. KẾ HOẠCH CÔNG VIỆC" (Planned)
```

---

## Advanced Usage

### Programmatic Usage
```python
from config import Settings, setup_logging
from repositories import GoogleSheetsClient
from services import ReportService

# Setup
setup_logging()
settings = Settings()
client = GoogleSheetsClient(settings)
service = ReportService(client)

# Import
result = service.import_from_excel(
    file_path="input/report.xlsx",
    employee_code="NV001",
    department_code="IT",
    auto_update=False
)

print(f"Report code: {result['report_code']}")
print(f"Total tasks: {result['total_tasks']}")
```

### Custom Parsing
```python
from parsers import ExcelParser
from pathlib import Path

# Parse Excel
parser = ExcelParser(Path("input/report.xlsx"))
data = parser.parse()

# Access parsed data
print(f"Period: {data['metadata']['period']}")
print(f"Actual tasks: {len(data['actual_functional_tasks'])}")
print(f"Planned tasks: {len(data['planned_functional_tasks'])}")
```

### Direct Repository Access
```python
from repositories import GoogleSheetsClient, EmployeeRepository

# Setup
client = GoogleSheetsClient()
employee_repo = EmployeeRepository(client)

# Query
all_employees = employee_repo.get_all()
it_employees = employee_repo.get_by_department("IT")
employee = employee_repo.get_by_code("NV001")
```

---

## File Structure Reference

```
Your Excel File Should Have:
├── Title (with period: "Từ ngày ... đến ngày ...")
├── Section 1: Công việc thực hiện
│   ├── 1. Công việc theo chức năng (Row 6)
│   └── 2. Công việc theo dự án (Dynamic row)
├── Section 2: Đánh giá
│   ├── 3.1 Công việc hằng ngày
│   └── 3.2 Chuyên môn
└── Section 3: Kế hoạch công việc
    ├── 1. Công việc theo chức năng
    └── 2. Công việc theo dự án

Google Sheets Structure:
├── Employees Sheet
├── Departments Sheet (auto-created if needed)
├── Work_Reports Sheet
├── Tasks_Actual Sheet
├── Tasks_Planned Sheet
└── Reviews Sheet
```

---

## Next Steps

1. **Test with your data:**
   ```bash
   python main.py import --file "input/your_report.xlsx" --employee "YOUR_CODE" --department "YOUR_DEPT"
   ```

2. **Check Google Sheets:**
   - Open your spreadsheet
   - Verify data in all sheets
   - Check task hierarchy (parent-child relationships)

3. **View the report:**
   ```bash
   python main.py view --report "RPT-YOUR_CODE-202409"
   ```

4. **Run validation:**
   ```bash
   python main.py validate
   ```

---

## Support

If you encounter issues:

1. **Check logs:**
   ```bash
   tail -f logs/app.log
   ```

2. **Enable debug mode:**
   ```env
   # In .env
   DEBUG=True
   LOG_LEVEL=DEBUG
   ```

3. **Test connection:**
   ```bash
   python test_connection.py
   ```

---

**Happy reporting! 🎉**
