# 🚀 Implementation Guide for Remaining Modules

This guide provides templates and examples for implementing the remaining modules.

## 📦 Parsers Module

### Create `parsers/__init__.py`:
```python
"""
Parsers Module

File parsing and data extraction
"""

from .excel_parser import ExcelParser
from .csv_parser import CSVParser
from .validators import DataValidator
from .transformers import DataTransformer

__all__ = [
    'ExcelParser',
    'CSVParser',
    'DataValidator',
    'DataTransformer'
]
```

### Create `parsers/base_parser.py`:
```python
"""Base Parser - Abstract parser class"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any
from pathlib import Path

class BaseParser(ABC):
    """Abstract base class for all parsers"""
    
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.validate_file()
    
    def validate_file(self) -> None:
        """Validate file exists"""
        if not self.file_path.exists():
            raise FileNotFoundError(f"File not found: {self.file_path}")
    
    @abstractmethod
    def parse(self) -> Dict[str, Any]:
        """Parse file and return structured data"""
        pass
    
    @abstractmethod
    def extract_metadata(self) -> Dict[str, Any]:
        """Extract file metadata"""
        pass
```

### Create `parsers/excel_parser.py`:
```python
"""Excel Parser - Parse work report Excel files"""

import pandas as pd
from openpyxl import load_workbook
from typing import Dict, List, Any
from pathlib import Path

from .base_parser import BaseParser
from models import ActualTask, PlannedTask
from utils import parse_date, parse_stt, extract_period_from_text
from config import EXCEL_SECTION_KEYWORDS

class ExcelParser(BaseParser):
    """Parse Excel work reports"""
    
    def __init__(self, file_path: Path, sheet_name: str = None):
        super().__init__(file_path)
        self.sheet_name = sheet_name
        self.workbook = None
        self.sheet = None
    
    def parse(self) -> Dict[str, Any]:
        """Parse Excel file"""
        self.workbook = load_workbook(self.file_path, data_only=True)
        self.sheet = self.workbook[self.sheet_name] if self.sheet_name else self.workbook.active
        
        # Extract metadata
        metadata = self.extract_metadata()
        
        # Find sections
        sections = self._find_sections()
        
        # Parse tasks
        actual_tasks = self._parse_actual_tasks(sections)
        planned_tasks = self._parse_planned_tasks(sections)
        
        # Parse reviews
        reviews = self._parse_reviews(sections)
        
        return {
            'metadata': metadata,
            'actual_tasks': actual_tasks,
            'planned_tasks': planned_tasks,
            'reviews': reviews
        }
    
    def extract_metadata(self) -> Dict[str, Any]:
        """Extract report period from title"""
        # Get title from first few rows
        title = ""
        for row in range(1, 10):
            cell_value = self.sheet.cell(row, 1).value
            if cell_value and "Từ ngày" in str(cell_value):
                title = str(cell_value)
                break
        
        # Extract period
        period = extract_period_from_text(title)
        
        return {
            'title': title,
            'period': period
        }
    
    def _find_sections(self) -> Dict[str, int]:
        """Find section start rows"""
        sections = {}
        # Implement section finding logic
        # (migrate from extractors/excel_reader.py)
        return sections
    
    def _parse_actual_tasks(self, sections: Dict) -> List[ActualTask]:
        """Parse actual tasks"""
        # Implement actual task parsing
        # (migrate from extractors/task_parser.py)
        return []
    
    def _parse_planned_tasks(self, sections: Dict) -> List[PlannedTask]:
        """Parse planned tasks"""
        # Implement planned task parsing
        return []
    
    def _parse_reviews(self, sections: Dict) -> Dict[str, str]:
        """Parse reviews section"""
        return {
            'daily_work': '',
            'professional': ''
        }
```

## 📊 Repositories Module

### Create `repositories/__init__.py`:
```python
"""
Repositories Module

Data access layer for Google Sheets
"""

from .google_sheets_client import GoogleSheetsClient
from .employee_repository import EmployeeRepository
from .report_repository import ReportRepository
from .task_repository import TaskRepository
from .review_repository import ReviewRepository

__all__ = [
    'GoogleSheetsClient',
    'EmployeeRepository',
    'ReportRepository',
    'TaskRepository',
    'ReviewRepository'
]
```

### Create `repositories/google_sheets_client.py`:
```python
"""Google Sheets Client - Wrapper for Google Sheets API"""

import gspread
from google.oauth2.service_account import Credentials
from gspread_dataframe import get_as_dataframe, set_with_dataframe
import pandas as pd
from typing import List, Dict, Any

from config import Settings, SheetName, COLUMN_MAPPINGS
from utils import get_logger, retry

logger = get_logger(__name__)

class GoogleSheetsClient:
    """Google Sheets API client"""
    
    def __init__(self, settings: Settings = None):
        self.settings = settings or Settings()
        self.client = None
        self.spreadsheet = None
        self._connect()
    
    @retry(max_attempts=3)
    def _connect(self) -> None:
        """Connect to Google Sheets"""
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        
        creds = Credentials.from_service_account_file(
            str(self.settings.get_credentials_path()),
            scopes=scope
        )
        
        self.client = gspread.authorize(creds)
        
        if self.settings.GOOGLE_SHEETS_SPREADSHEET_ID:
            self.spreadsheet = self.client.open_by_key(
                self.settings.GOOGLE_SHEETS_SPREADSHEET_ID
            )
        else:
            self.spreadsheet = self.client.open(
                self.settings.GOOGLE_SHEETS_SPREADSHEET_NAME
            )
        
        logger.info(f"Connected to spreadsheet: {self.spreadsheet.title}")
        
        # Initialize sheets
        self._initialize_sheets()
    
    def _initialize_sheets(self) -> None:
        """Create sheets if they don't exist"""
        existing_sheets = [ws.title for ws in self.spreadsheet.worksheets()]
        
        for sheet_name in SheetName:
            if sheet_name.value not in existing_sheets:
                self._create_sheet(sheet_name)
    
    def _create_sheet(self, sheet_name: SheetName) -> None:
        """Create a new sheet with headers"""
        headers = COLUMN_MAPPINGS[sheet_name]
        worksheet = self.spreadsheet.add_worksheet(
            title=sheet_name.value,
            rows=1000,
            cols=len(headers)
        )
        worksheet.update('A1', [headers])
        logger.info(f"Created sheet: {sheet_name.value}")
    
    def get_worksheet(self, sheet_name: SheetName):
        """Get worksheet by name"""
        return self.spreadsheet.worksheet(sheet_name.value)
    
    def read_sheet(self, sheet_name: SheetName) -> pd.DataFrame:
        """Read sheet as DataFrame"""
        worksheet = self.get_worksheet(sheet_name)
        df = get_as_dataframe(worksheet, evaluate_formulas=True)
        return df.dropna(how='all')
    
    def write_sheet(self, sheet_name: SheetName, df: pd.DataFrame) -> None:
        """Write DataFrame to sheet"""
        worksheet = self.get_worksheet(sheet_name)
        set_with_dataframe(worksheet, df)
```

### Create `repositories/base_repository.py`:
```python
"""Base Repository - Abstract CRUD operations"""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Optional, Dict, Any
import pandas as pd

from config import SheetName
from models import BaseModel
from utils import get_logger

T = TypeVar('T', bound=BaseModel)
logger = get_logger(__name__)

class BaseRepository(ABC, Generic[T]):
    """Abstract base repository for CRUD operations"""
    
    def __init__(self, client, sheet_name: SheetName):
        self.client = client
        self.sheet_name = sheet_name
    
    @abstractmethod
    def model_to_dict(self, model: T) -> Dict[str, Any]:
        """Convert model to dictionary for storage"""
        pass
    
    @abstractmethod
    def dict_to_model(self, data: Dict[str, Any]) -> T:
        """Convert dictionary to model"""
        pass
    
    def create(self, model: T) -> T:
        """Create new record"""
        df = self.client.read_sheet(self.sheet_name)
        new_row = pd.DataFrame([self.model_to_dict(model)])
        df = pd.concat([df, new_row], ignore_index=True)
        self.client.write_sheet(self.sheet_name, df)
        logger.info(f"Created record in {self.sheet_name.value}")
        return model
    
    def find_by_id(self, id_field: str, id_value: str) -> Optional[T]:
        """Find record by ID"""
        df = self.client.read_sheet(self.sheet_name)
        if df.empty or id_field not in df.columns:
            return None
        
        result = df[df[id_field] == id_value]
        if result.empty:
            return None
        
        return self.dict_to_model(result.iloc[0].to_dict())
    
    def find_all(self, filters: Dict[str, Any] = None) -> List[T]:
        """Find all records with optional filters"""
        df = self.client.read_sheet(self.sheet_name)
        
        if filters:
            for key, value in filters.items():
                if key in df.columns:
                    df = df[df[key] == value]
        
        return [self.dict_to_model(row.to_dict()) for _, row in df.iterrows()]
    
    def update(self, id_field: str, id_value: str, model: T) -> bool:
        """Update existing record"""
        df = self.client.read_sheet(self.sheet_name)
        
        if id_field not in df.columns:
            return False
        
        idx = df[df[id_field] == id_value].index
        if len(idx) == 0:
            return False
        
        updated_data = self.model_to_dict(model)
        for key, value in updated_data.items():
            if key in df.columns:
                df.at[idx[0], key] = value
        
        self.client.write_sheet(self.sheet_name, df)
        logger.info(f"Updated record in {self.sheet_name.value}")
        return True
    
    def delete(self, id_field: str, id_value: str) -> bool:
        """Delete record"""
        df = self.client.read_sheet(self.sheet_name)
        
        if id_field not in df.columns:
            return False
        
        df = df[df[id_field] != id_value]
        self.client.write_sheet(self.sheet_name, df)
        logger.info(f"Deleted record from {self.sheet_name.value}")
        return True
```

## 🎯 Services Module

### Create `services/__init__.py`:
```python
"""
Services Module

Business logic layer
"""

from .report_service import ReportService
from .task_service import TaskService
from .validation_service import ValidationService

__all__ = [
    'ReportService',
    'TaskService',
    'ValidationService'
]
```

### Create `services/report_service.py`:
```python
"""Report Service - Report processing orchestration"""

from pathlib import Path
from typing import Dict, Any

from parsers import ExcelParser
from repositories import GoogleSheetsClient, ReportRepository, TaskRepository
from models import WorkReport, ActualTask, PlannedTask
from utils import get_logger

logger = get_logger(__name__)

class ReportService:
    """Service for processing work reports"""
    
    def __init__(self, client: GoogleSheetsClient):
        self.client = client
        self.report_repo = ReportRepository(client)
        self.task_repo = TaskRepository(client)
    
    def import_from_excel(self, file_path: str, sheet_name: str = None) -> WorkReport:
        """Import report from Excel file"""
        logger.info(f"Importing report from: {file_path}")
        
        # Parse Excel
        parser = ExcelParser(Path(file_path), sheet_name)
        data = parser.parse()
        
        # Create report model
        report = self._create_report_model(data)
        
        # Save to Google Sheets
        self.report_repo.create(report)
        
        # Save tasks
        for task in data['actual_tasks']:
            self.task_repo.create_actual_task(task)
        
        for task in data['planned_tasks']:
            self.task_repo.create_planned_task(task)
        
        logger.info(f"Successfully imported report: {report.report_code}")
        return report
    
    def _create_report_model(self, data: Dict[str, Any]) -> WorkReport:
        """Create WorkReport model from parsed data"""
        # Implement model creation logic
        pass
```

## 🏃 Usage Example

```python
# main.py
from config import Settings, setup_logging
from repositories import GoogleSheetsClient
from services import ReportService

def main():
    # Setup
    setup_logging()
    settings = Settings()
    settings.ensure_directories()
    
    # Validate settings
    is_valid, error = settings.validate()
    if not is_valid:
        print(f"Configuration error: {error}")
        return
    
    # Initialize
    client = GoogleSheetsClient(settings)
    report_service = ReportService(client)
    
    # Process report
    report = report_service.import_from_excel(
        "input/baocao_NV001.xlsx",
        "Th8-T9"
    )
    
    print(f"✅ Imported: {report.report_code}")

if __name__ == "__main__":
    main()
```

## 📝 Next Steps

1. Implement remaining parsers methods
2. Complete repository implementations
3. Complete service implementations
4. Add comprehensive tests
5. Update main.py with CLI interface
6. Update documentation

---

**This guide provides the skeleton. Migrate existing logic from old files to match this structure.**
