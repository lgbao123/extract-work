"""
Excel Parser

Parse work report Excel files
"""

import pandas as pd
from openpyxl import load_workbook
from typing import Dict, List, Any, Optional
from pathlib import Path
import uuid

from .base_parser import BaseParser
from .transformers import DataTransformer
from models import ActualTask, PlannedTask, ReportPeriod
from utils import (
    ParsingError, 
    extract_period_from_text, 
    parse_date, 
    parse_stt,
    clean_string,
    get_logger
)
from config.constants import EXCEL_SECTION_KEYWORDS, TaskCategory

logger = get_logger(__name__)


class ExcelParser(BaseParser):
    """Parse Excel work reports"""
    
    def __init__(self, file_path: Path, sheet_name: Optional[str] = None):
        """
        Initialize Excel parser
        
        Args:
            file_path: Path to Excel file
            sheet_name: Name of sheet to parse (default: active sheet)
        """
        super().__init__(file_path)
        self.sheet_name = sheet_name
        self.workbook = None
        self.sheet = None
        self.transformer = DataTransformer()
    
    def parse(self) -> Dict[str, Any]:
        """
        Parse Excel file and extract all data
        
        Returns:
            Dictionary with metadata, tasks, and reviews
        """
        logger.info(f"Parsing Excel file: {self.file_path}")
        
        try:
            # Load workbook
            self.workbook = load_workbook(str(self.file_path), data_only=True)
            self.sheet_name = sorted(list(self.workbook.sheetnames), reverse=True)[0]
            self.sheet = (self.workbook[self.sheet_name] 
                         if self.sheet_name 
                         else self.workbook.active)
            
            # Extract metadata
            metadata = self.extract_metadata()
            
            # Find sections
            sections = self._find_sections()
            
            # Parse tasks
            actual_functional = self._parse_actual_functional_tasks(sections)
            actual_project = self._parse_actual_project_tasks(sections)
            planned_functional = self._parse_planned_functional_tasks(sections)
            planned_project = self._parse_planned_project_tasks(sections)
            
            # Parse reviews
            reviews = self._parse_reviews(sections)
            
            # Establish task hierarchy
            actual_functional = self._establish_hierarchy(actual_functional)
            actual_project = self._establish_hierarchy(actual_project)
            planned_functional = self._establish_hierarchy(planned_functional)
            planned_project = self._establish_hierarchy(planned_project)
            
            result = {
                'metadata': metadata,
                'actual_functional_tasks': actual_functional,
                'actual_project_tasks': actual_project,
                'planned_functional_tasks': planned_functional,
                'planned_project_tasks': planned_project,
                'reviews': reviews
            }
            
            logger.info(
                f"Parsed {len(actual_functional)} actual functional, "
                f"{len(actual_project)} actual project, "
                f"{len(planned_functional)} planned functional, "
                f"{len(planned_project)} planned project tasks"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to parse Excel file: {e}")
            raise ParsingError(f"Excel parsing failed: {e}") from e
        finally:
            if self.workbook:
                self.workbook.close()
    
    def extract_metadata(self) -> Dict[str, Any]:
        """Extract report period from title"""
        title = ""
        
        # Search first 10 rows for title
        for row in range(1, 11):
            cell_values = [self.sheet.cell(row, col).value for col in range(1, 8)]
            cell_value = " ".join([str(cv) for cv in cell_values if cv is not None])
            if cell_value and "Từ ngày" in str(cell_value):
                title = str(cell_value)
                break
        
        if not title:
            raise ParsingError("Could not find report period in Excel file")
        
        # Extract period
        try:
            period_data = extract_period_from_text(title)
            period = ReportPeriod(**period_data)
        except Exception as e:
            raise ParsingError(f"Failed to extract period: {e}") from e
        
        # Extract employee name from first 10 rows
        employee_name = ""
        for row in range(1, 11):
            # Check multiple columns for employee name
            # for col in range(1, 5):
            #     cell_value = str(self.sheet.cell(row, col).value or "")
            cell_values = [self.sheet.cell(row, col).value for col in range(1, 8)]
            cell_value = " ".join([str(cv) for cv in cell_values if cv is not None])
            # Extract name after "Nhân viên:" or " - Nhân Viên"
            if "nhân viên:" in str.lower(cell_value):
                employee_name = clean_string(cell_value.split(":")[1])
            elif "- nhân viên" in str.lower(cell_value):
                employee_name = clean_string(cell_value.split("-")[0].split(".")[-1])
            if employee_name:
                break
            # if employee_name:
            #     break
        
        return {
            'title': title,
            'period': period,
            'employee_name': employee_name
        }
        
    
    def _find_sections(self) -> Dict[str, Optional[int]]:
        """
        Find section start rows in Excel
        
        Returns:
            Dictionary mapping section names to row numbers
        """
        sections = {
            'actual': None,
            'actual_functional': None,
            'actual_project': None,
            'actual_review': None,
            'planned': None,
            'planned_functional': None,
            'planned_project': None
        }
        
        keywords = EXCEL_SECTION_KEYWORDS
        
        # Scan all rows
        for row_idx in range(1, self.sheet.max_row + 1):
            cell_value = self.sheet.cell(row_idx, 1).value
            row_value = ' '.join([str(cell.value) for cell in self.sheet[row_idx] if cell.value is not None])
            if not row_value:
                continue
            
            cell_str = str(cell_value).strip()
            row_str = row_value.strip()
            # Check each keyword
            for key, keywords_list in keywords.items():
                # Support both string and list of keywords
                if isinstance(keywords_list, str):
                    keywords_list = [keywords_list]
                
                # Check if any keyword matches
                for keyword in keywords_list:
                    if str.lower(keyword) in str.lower(row_str) and sections[key] is None:
                        if row_idx not in sections.values():
                            sections[key] = row_idx
                            logger.debug(f"Found section '{key}' at row {row_idx}")
                            break  # Stop checking other keywords once found
        
        logger.debug(f"Sections found: {sections}")
        return sections
    
    def _parse_actual_functional_tasks(self, sections: Dict) -> List[ActualTask]:
        """Parse actual functional tasks"""
        if not sections['actual_functional']:
            return []
        
        header_row = sections['actual'] + 1 
        start_row = sections['actual_functional'] + 1
        end_row = sections['actual_project'] - 1

        return self._parse_task_section(start_row, end_row, header_row, 'actual', TaskCategory.FUNCTIONAL)

    def _parse_actual_project_tasks(self, sections: Dict) -> List[ActualTask]:
        """Parse actual project tasks"""
        if not sections['actual_project']:
            return []

        header_row = sections['actual'] + 1
        start_row = sections['actual_project'] + 1
        end_row = sections['actual_review'] - 1  if sections['actual_review'] else sections['planned'] -1

        return self._parse_task_section(start_row, end_row, header_row, 'actual', TaskCategory.PROJECT)

    def _parse_planned_functional_tasks(self, sections: Dict) -> List[PlannedTask]:
        """Parse planned functional tasks"""
        if not sections['planned_functional']:
            return []
        
        header_row = sections['planned'] + 1
        start_row = sections['planned_functional'] + 1
        end_row = sections['planned_project'] - 1

        return self._parse_task_section(start_row, end_row, header_row, 'planned', TaskCategory.FUNCTIONAL)

    def _parse_planned_project_tasks(self, sections: Dict) -> List[PlannedTask]:
        """Parse planned project tasks"""
        if not sections['planned_project']:
            return []
        
        header_row = sections['planned'] + 1
        start_row = sections['planned_project'] + 1
        end_row = self.sheet.max_row

        return self._parse_task_section(start_row, end_row, header_row, 'planned', TaskCategory.PROJECT)

    def _parse_task_section(self, start_row: int, end_row: int, header_row: int, 
                           task_type: str, category: TaskCategory) -> List:
        """
        Parse tasks from a section
        
        Args:
            start_row: Starting row number
            end_row: Ending row number
            task_type: 'actual' or 'planned'
            category: Task category
            
        Returns:
            List of Task objects
        """
        tasks = []
        
        # Read section as DataFrame using pandas
        try:
            df = pd.read_excel(
                str(self.file_path),
                sheet_name=self.sheet_name or 0,
                skiprows=header_row - 1 ,  # Skip to data rows
                header=[0, 1],  # Multi-level header
                nrows=(end_row - header_row) - 1,
                dtype={'Stt': str, 'Unnamed: 0_level_1': str}  # Force STT to be read as string
            )
            # Adjust DataFrame to start from correct row
            df = df.iloc[(start_row - header_row) - 2:]
            # Flatten column names
            df = self.transformer.flatten_multiindex_columns(df)
            
            # Clean DataFrame
            df = df.dropna(subset=[df.columns[1]])
            
            # Parse each row
            for idx, row in df.iterrows():
                task = self._parse_task_row(row, task_type, category)
                if task:
                    tasks.append(task)
                    
        except Exception as e:
            logger.warning(f"Error parsing task section: {e}")
        
        return tasks
    
    def _parse_task_row(self, row: pd.Series, task_type: str, 
                       category: TaskCategory) -> Optional[Any]:
        """Parse a single task row"""
        # Get STT
        stt = clean_string(str(row.get('Stt', row.get('Unnamed: 0_level_1', ''))))
        if not stt or stt == 'nan':
            return None
        
        # Basic task data
        task_id = str(uuid.uuid4())
        task_name = clean_string(str(row.get('Công việc', '')))
        task_type_val = clean_string(str(row.get('Loại công việc', '')))
        
        # Handle "Từ" column - can be date or frequency
        from_value = row.get('Thời gian thực hiện_Từ', '')
        start_date = None
        frequency = None
        
        # Try to parse as date first
        parsed_date = parse_date(from_value)
        if parsed_date:
            start_date = parsed_date
        else:
            # If not a date, treat as frequency text
            freq_str = clean_string(str(from_value))
            if freq_str and freq_str.lower() != 'nan' and freq_str.lower() != 'none':
                frequency = freq_str
        
        # End date
        end_date = parse_date(row.get('Thời gian thực hiện_Đến', ''))
        
        # Description, Result
        # description = clean_string(str(row.get('Mô tả yêu cầu, giải pháp để thực hiện', '')))
        # result = clean_string(str(row.get('Kết quả thực hiện', '')))
        
        # Parse STT for level
        level, parent_stt = parse_stt(stt)
        
        # Common task data
        task_data = {
            'task_id': task_id,
            'report_code': '',  # Will be set later
            'stt': stt,
            'task_name': task_name,
            'task_type': task_type_val,
            'category': category,
            'start_date': start_date.strftime('%Y-%m-%d') if start_date else None,
            'end_date': end_date.strftime('%Y-%m-%d') if end_date else None,
            'frequency': frequency,
            # 'result': result,
            'level': level,
            'parent_task_id': None,  # Will be set in hierarchy establishment
            'has_subtasks': False,
            'subtask_count': 0
        }
        
        # Create appropriate task type
        if task_type == 'actual':
            evaluation = clean_string(str(row.get('Đ/G KQ', '')))
            challenges = clean_string(str(row.get('Đánh giá khó khăn thuận lợi/Tồn đọng', '')))
            result = clean_string(str(row.get('Kết quả thực hiện', '')))
            return ActualTask(**task_data, evaluation=evaluation, challenges=challenges, results=result)
        else:
            description_value = row.get('Mô tả yêu cầu, giải pháp để thực hiện', '')
            if isinstance(description_value, pd.Series):
                description = clean_string(str(description_value.iloc[0] if len(description_value) > 0 else ''))
            else:
                description = clean_string(str(description_value))
   
            cost_str = clean_string(str(row.get('Chi phí thực hiện (VNĐ)')))
            cost = self.transformer.parse_cost(cost_str)
            return PlannedTask(**task_data, description=description, cost=cost, cost_unit='VND')
    
    def _establish_hierarchy(self, tasks: List) -> List:
        """
        Establish parent-child relationships between tasks
        
        Args:
            tasks: List of tasks
            
        Returns:
            List of tasks with hierarchy established
        """
        if not tasks:
            return tasks
        
        # Create STT to task mapping
        stt_map = {task.stt: task for task in tasks}
        
        # Establish parent relationships
        for task in tasks:
            if task.level > 0:
                parent_stt = task.get_parent_stt()
                if parent_stt and parent_stt in stt_map:
                    parent_task = stt_map[parent_stt]
                    task.parent_task_id = parent_task.task_id
                    parent_task.has_subtasks = True
        
        # Count subtasks
        for task in tasks:
            if task.has_subtasks:
                task.subtask_count = sum(
                    1 for t in tasks 
                    if t.parent_task_id == task.task_id
                )
        
        return tasks
    
    def _parse_reviews(self, sections: Dict) -> Dict[str, str]:
        """Parse review section"""
        reviews = {
            'daily_work': '',
            'professional': ''
        }
        
        if not sections.get('actual_review'):
            return reviews
        
        start_row = sections['actual_review']
        end_row = sections['planned'] if sections['planned'] else self.sheet.max_row
        
        # Look for review text in this section
        for row_idx in range(start_row, min(start_row + 20, end_row)):
            cell_value = self.sheet.cell(row_idx, 1).value
            if not cell_value:
                continue
            
            cell_str = str(cell_value).strip()
            
            if '3.1' in cell_str or 'công việc hằng ngày' in cell_str.lower():
                # Get next few cells for content
                reviews['daily_work'] = clean_string(str(self.sheet.cell(row_idx + 1, 1).value or ''))
            
            if '3.2' in cell_str or 'chuyên môn' in cell_str.lower():
                reviews['professional'] = clean_string(str(self.sheet.cell(row_idx + 1, 1).value or ''))
        
        return reviews
