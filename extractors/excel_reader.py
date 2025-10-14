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
        'actual': None,
        'actual_functional': None,
        'actual_project': None,
        'actual_review': None,
        'planned': None,
        'planned_functional': None,
        'planned_project': None
    }
    
    # Flags to track which main section we're currently in
    in_actual_section = False
    in_planned_section = False
    
    for row_idx, row in enumerate(sheet.iter_rows(min_row=1)):
        # Check first few columns for section keywords
        cell_values = []
        for col_idx in range(min(5, len(row))):  # Check first 5 columns
            cell_value = str(row[col_idx].value or "").strip()
            cell_values.append(cell_value)
        
        # Combine all cell values to check for keywords
        combined_text = " ".join(cell_values).upper()
        
        # Check for main section headers
        if EXCEL_SECTION_KEYWORDS["actual"].upper() in combined_text:
            sections['actual'] = row_idx
            in_actual_section = True
            in_planned_section = False
            continue
            
        if EXCEL_SECTION_KEYWORDS["planned"].upper() in combined_text:
            sections['planned'] = row_idx
            in_planned_section = True
            in_actual_section = False
            continue
        
        # Check for subsection headers within main sections
        if EXCEL_SECTION_KEYWORDS["actual_functional"].upper() in combined_text:
            if in_actual_section and sections['actual_functional'] is None:
                sections['actual_functional'] = row_idx  # Skip header and start from data rows
            elif in_planned_section and sections['planned_functional'] is None:
                sections['planned_functional'] = row_idx 
                
        if EXCEL_SECTION_KEYWORDS["actual_project"].upper() in combined_text:
            if in_actual_section and sections['actual_project'] is None:
                sections['actual_project'] = row_idx 
            elif in_planned_section and sections['planned_project'] is None:
                sections['planned_project'] = row_idx
                
        if EXCEL_SECTION_KEYWORDS["actual_review"].upper() in combined_text:
            if in_actual_section and sections['actual_review'] is None:
                sections['actual_review'] = row_idx 
    return sections


def load_excel_file(excel_path: str, sheet_name: str):
    """
    Load Excel file
    
    Args:
        excel_path: Đường dẫn file Excel
        
    Returns:
        (workbook, sheet, title)
    """
    wb = load_workbook(excel_path, data_only=True)
    sheet = wb[sheet_name]
    title = sheet['C1'].value or ""
    title = " ".join(title.split())
    return wb, sheet, title