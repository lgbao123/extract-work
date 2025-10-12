from typing import Dict
from openpyxl import load_workbook
from config.settings import EXCEL_SECTION_KEYWORDS


def find_section_start_rows(sheet) -> Dict[str, int]:
    """
    Tìm vị trí bắt đầu của các section trong Excel
    
    Args:
        sheet: openpyxl worksheet
        
    Returns:
        Dict với key là tên section và value là row number
    """
    sections = {
        'actual_functional': None,
        'actual_project': None,
        'planned_functional': None,
        'planned_project': None
    }
    
    for row_idx, row in enumerate(sheet.iter_rows(min_row=1), start=1):
        cell_value = str(row[0].value or "").strip().upper()
        
        # Phần A - Thực hiện
        if EXCEL_SECTION_KEYWORDS["actual_functional"] in cell_value and sections['actual_functional'] is None:
            sections['actual_functional'] = row_idx + 2
        elif EXCEL_SECTION_KEYWORDS["actual_project"] in cell_value and sections['actual_project'] is None:
            sections['actual_project'] = row_idx + 2
        
        # Phần B - Kế hoạch  
        elif EXCEL_SECTION_KEYWORDS["planned_functional"] in cell_value and sections['planned_functional'] is None:
            sections['planned_functional'] = row_idx + 2
    
    return sections


def load_excel_file(excel_path: str):
    """
    Load Excel file
    
    Args:
        excel_path: Đường dẫn file Excel
        
    Returns:
        (workbook, sheet, title)
    """
    wb = load_workbook(excel_path, data_only=True)
    sheet = wb.active
    title = sheet['A1'].value or ""
    
    return wb, sheet, title