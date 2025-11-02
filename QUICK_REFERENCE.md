# 🚀 Quick Reference Card

## 📦 Import Patterns

### Config
```python
from config import Settings, SheetName, ReportStatus, setup_logging
from config.constants import TaskCategory, DATE_FORMATS
```

### Models
```python
from models import Employee, WorkReport, ActualTask, PlannedTask, Review
```

### Utils
```python
from utils import (
    parse_date, format_date, extract_period_from_text,
    clean_string, normalize_code, parse_stt, parse_cost,
    ValidationError, ParsingError, RepositoryError,
    retry, timing, rate_limit, get_logger
)
```

### Repositories
```python
from repositories import (
    GoogleSheetsClient,
    EmployeeRepository,
    ReportRepository,
    TaskRepository
)
```

### Services
```python
from services import ReportService, TaskService, ValidationService
```

## 💻 Common Code Patterns

### 1. Initialize Application
```python
from config import Settings, setup_logging
from repositories import GoogleSheetsClient

# Setup
setup_logging()
settings = Settings()
settings.ensure_directories()

# Validate
is_valid, error = settings.validate()
if not is_valid:
    print(f"Error: {error}")
    exit(1)

# Connect
client = GoogleSheetsClient(settings)
```

### 2. Create Models
```python
from models import Employee, WorkReport
from datetime import datetime

# Employee
employee = Employee(
    employee_code="NV001",
    full_name="Nguyễn Văn A",
    email="a.nguyen@company.com",
    department_code="IT"
)

# Work Report
report = WorkReport(
    report_code="BC-2025-09-NV001",
    employee_code="NV001",
    employee_name="Nguyễn Văn A",
    report_period_year=2025,
    report_period_month=9
)
```

### 3. Parse Data
```python
from utils import parse_date, parse_stt, parse_cost

# Parse date
date = parse_date("20/08/2025")  # → datetime(2025, 8, 20)

# Parse STT
level, parent = parse_stt("1.2.3")  # → (2, "1.2")

# Parse cost
cost = parse_cost("1,000,000 VND")  # → 1000000.0
```

### 4. Use Repository
```python
from repositories import EmployeeRepository
from models import Employee

repo = EmployeeRepository(client)

# Create
employee = Employee(...)
repo.create(employee)

# Find
employee = repo.find_by_code("NV001")

# Update
employee.email = "new@email.com"
repo.update("NV001", employee)

# Delete
repo.delete("NV001")
```

### 5. Use Decorators
```python
from utils import retry, timing, rate_limit

@retry(max_attempts=3, delay=2.0)
def fetch_data():
    # Will retry 3 times with 2s delay
    pass

@timing
def process_data():
    # Will log execution time
    pass

@rate_limit(calls_per_period=10, period=60)
def api_call():
    # Max 10 calls per minute
    pass
```

### 6. Handle Errors
```python
from utils import ValidationError, ParsingError, RepositoryError

try:
    # Your code
    pass
except ValidationError as e:
    logger.error(f"Validation failed: {e}")
except ParsingError as e:
    logger.error(f"Parsing failed: {e}")
except RepositoryError as e:
    logger.error(f"Database error: {e}")
```

### 7. Log Messages
```python
from utils import get_logger

logger = get_logger(__name__)

logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
logger.critical("Critical message")
```

## 📋 File Templates

### Create a New Model
```python
"""
ModelName Model

Description
"""

from dataclasses import dataclass
from typing import Optional

from .base import BaseModel

@dataclass
class ModelName(BaseModel):
    """Model description"""
    
    field1: str
    field2: Optional[str] = None
    
    def __post_init__(self):
        """Validate and normalize"""
        self.field1 = self.field1.strip()
    
    def __str__(self) -> str:
        return f"ModelName({self.field1})"
```

### Create a New Repository
```python
"""
ModelName Repository

CRUD operations for ModelName
"""

from typing import Optional, List

from .base_repository import BaseRepository
from models import ModelName
from config import SheetName

class ModelNameRepository(BaseRepository[ModelName]):
    """Repository for ModelName"""
    
    def __init__(self, client):
        super().__init__(client, SheetName.MODEL_SHEET)
    
    def model_to_dict(self, model: ModelName) -> dict:
        """Convert model to dict"""
        return model.to_dict()
    
    def dict_to_model(self, data: dict) -> ModelName:
        """Convert dict to model"""
        return ModelName.from_dict(data)
    
    def find_by_code(self, code: str) -> Optional[ModelName]:
        """Find by code"""
        return self.find_by_id('code_field', code)
```

### Create a New Service
```python
"""
Service Name

Business logic for ...
"""

from typing import List, Optional

from repositories import ModelRepository
from models import Model
from utils import get_logger, ValidationError

logger = get_logger(__name__)

class ServiceName:
    """Service for ..."""
    
    def __init__(self, client):
        self.repo = ModelRepository(client)
    
    def process(self, data):
        """Process data"""
        logger.info("Processing...")
        
        # Validate
        self._validate(data)
        
        # Transform
        model = self._transform(data)
        
        # Save
        self.repo.create(model)
        
        logger.info("Complete")
        return model
    
    def _validate(self, data):
        """Validate data"""
        if not data:
            raise ValidationError("Data is empty")
    
    def _transform(self, data):
        """Transform data to model"""
        return Model(**data)
```

## 🔍 Common Tasks

### Import Excel Report
```python
from services import ReportService

service = ReportService(client)
report = service.import_from_excel(
    "input/baocao_NV001.xlsx",
    "Th8-T9"
)
```

### Query Data
```python
from repositories import ReportRepository

repo = ReportRepository(client)

# Get all reports for employee
reports = repo.find_all({
    'employee_code': 'NV001',
    'report_period_year': 2025
})

# Get specific report
report = repo.find_by_code('BC-2025-09-NV001')
```

### Validate Settings
```python
from config import Settings

settings = Settings()
is_valid, error = settings.validate()
if not is_valid:
    print(f"Configuration error: {error}")
```

## 🛠️ Debug Commands

### Check Connection
```python
python test_connection.py
```

### Run with Debug Logging
```python
# Set in .env
DEBUG=True
LOG_LEVEL=DEBUG
```

### Test Import
```python
python -c "from config import Settings; print(Settings().BASE_DIR)"
python -c "from models import Employee; e = Employee('NV001', 'Test'); print(e)"
python -c "from utils import parse_date; print(parse_date('20/08/2025'))"
```

## 📚 Quick Links

- **Full Code Templates**: `IMPLEMENTATION_GUIDE.md`
- **Architecture Overview**: `RESTRUCTURING_GUIDE.md`
- **Setup Instructions**: `SETUP_GUIDE.md`
- **Migration Guide**: `MIGRATION_GUIDE.md`

---

**Keep this card handy for quick reference!**
