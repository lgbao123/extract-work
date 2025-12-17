# Model Conversions Implementation

## Summary

Completed the abstract methods `model_to_dict()` and `dict_to_model()` in the repository pattern by implementing `to_sheet_dict()` and `from_dict()` methods in the model classes.

## Changes Made

### 1. Employee Model (`models/employee.py`)

Added two methods:

#### `to_sheet_dict()` 
Converts Employee model to dictionary with camelCase keys for Google Sheets:
- `employee_code` → `employeeCode`
- `full_name` → `fullName`
- `department_code` → `departmentCode`
- etc.

#### `from_dict()`
Creates Employee instance from dictionary, handling both camelCase (from Sheets) and snake_case (Python):
- Normalizes keys to snake_case
- Handles timestamp string conversion
- Supports both naming conventions

### 2. Department Model (`models/department.py`)

Added the same two methods following the same pattern:

#### `to_sheet_dict()`
Converts Department model to camelCase dictionary:
- `department_code` → `departmentCode`
- `department_name` → `departmentName`
- `parent_department_code` → `parentDepartmentCode`

#### `from_dict()`
Creates Department from dict with key normalization and timestamp handling.

## How It Works

### Writing to Google Sheets
```python
employee = Employee(
    employee_code="NV001",
    full_name="Nguyen Van A",
    email="a.nguyen@company.com",
    department_code="IT"
)

# Repository calls model_to_dict() which calls to_sheet_dict()
sheet_data = employee.to_sheet_dict()
# Returns: {'employeeCode': 'NV001', 'fullName': 'Nguyen Van A', ...}
```

### Reading from Google Sheets
```python
# Google Sheets returns camelCase data
sheet_row = {
    'employeeCode': 'NV001',
    'fullName': 'Nguyen Van A',
    'departmentCode': 'IT',
    'createdAt': '2025-12-10 10:30:00'
}

# Repository calls dict_to_model() which calls from_dict()
employee = Employee.from_dict(sheet_row)
# employee.employee_code = 'NV001'
# employee.full_name = 'Nguyen Van A'
# employee.created_at = datetime(2025, 12, 10, 10, 30, 0)
```

## Repository Usage

The base repository methods now work correctly:

```python
from repositories import EmployeeRepository, DepartmentRepository
from repositories.google_sheets_client import GoogleSheetsClient

client = GoogleSheetsClient(...)
emp_repo = EmployeeRepository(client)

# Create
employee = Employee(employee_code="NV001", full_name="Test User")
emp_repo.create(employee)  # Calls to_sheet_dict() internally

# Read
employee = emp_repo.get_by_id("NV001")  # Calls from_dict() internally
```

## Schema Alignment

The methods align with Google Sheets column definitions in `config/constants.py`:

**SHEET_EMPLOYEES columns:**
- employeeCode, fullName, email, departmentCode, departmentName, position, managerCode, createdAt, updatedAt

**SHEET_DEPARTMENTS columns:**
- departmentCode, departmentName, managerCode, parentDepartmentCode, createdAt, updatedAt

## Testing

Both model files compile without syntax errors:
```powershell
python -m py_compile models/employee.py
python -m py_compile models/department.py
```

To test the conversions in your actual code, use the repository methods which will automatically invoke these conversion methods.
