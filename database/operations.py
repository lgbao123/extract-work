from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd
import uuid
from gspread_dataframe import get_as_dataframe, set_with_dataframe
from config.settings import (
    SHEET_EMPLOYEES,
    SHEET_WORK_REPORTS,
    SHEET_TASKS_ACTUAL,
    SHEET_TASKS_PLANNED,
    SHEET_REVIEWS,
    DEFAULT_REPORT_STATUS
)


def insert_employee(spreadsheet, employee_data: Dict) -> Dict:
    """
    Thêm nhân viên mới hoặc lấy thông tin nếu đã tồn tại
    
    Args:
        spreadsheet: gspread Spreadsheet object
        employee_data: Dict thông tin nhân viên
        
    Returns:
        Dict employee
    """
    try:
        worksheet = spreadsheet.worksheet(SHEET_EMPLOYEES)
        
        # Đọc dữ liệu hiện tại
        df = get_as_dataframe(worksheet, evaluate_formulas=True)
        df = df.dropna(how='all')  # Xóa rows trống
        
        # Kiểm tra employee đã tồn tại
        if not df.empty and 'employeeCode' in df.columns:
            existing = df[df['employeeCode'] == employee_data['employeeCode']]
            if not existing.empty:
                print(f"→ Nhân viên đã tồn tại: {employee_data['employeeCode']}")
                return existing.iloc[0].to_dict()
        
        # Thêm timestamps
        employee_data['createdAt'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        employee_data['updatedAt'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Thêm nhân viên mới
        new_row = pd.DataFrame([employee_data])
        df = pd.concat([df, new_row], ignore_index=True)
        
        # Update sheet
        set_with_dataframe(worksheet, df)
        
        print(f"✓ Đã thêm nhân viên: {employee_data['employeeCode']} - {employee_data.get('fullName', '')}")
        return employee_data
        
    except Exception as e:
        print(f"✗ Lỗi thêm nhân viên: {e}")
        raise


def get_employee_by_code(spreadsheet, employee_code: str) -> Optional[Dict]:
    """
    Lấy thông tin nhân viên theo mã
    
    Args:
        spreadsheet: gspread Spreadsheet object
        employee_code: Mã nhân viên
        
    Returns:
        Dict employee hoặc None
    """
    try:
        worksheet = spreadsheet.worksheet(SHEET_EMPLOYEES)
        df = get_as_dataframe(worksheet, evaluate_formulas=True)
        df = df.dropna(how='all')
        
        if df.empty or 'employeeCode' not in df.columns:
            return None
            
        result = df[df['employeeCode'] == employee_code]
        if result.empty:
            return None
            
        return result.iloc[0].to_dict()
    except Exception as e:
        print(f"✗ Lỗi lấy thông tin nhân viên: {e}")
        return None


def insert_work_report(spreadsheet, work_report: Dict, auto_update: bool = False) -> bool:
    """
    Thêm báo cáo công việc
    
    Args:
        spreadsheet: gspread Spreadsheet object
        work_report: Dict báo cáo
        auto_update: Tự động update nếu đã tồn tại
        
    Returns:
        True nếu thành công
    """
    try:
        worksheet = spreadsheet.worksheet(SHEET_WORK_REPORTS)
        df = get_as_dataframe(worksheet, evaluate_formulas=True)
        df = df.dropna(how='all')
        
        # Kiểm tra báo cáo đã tồn tại
        existing = None
        if not df.empty and 'reportCode' in df.columns:
            existing_df = df[df['reportCode'] == work_report['reportCode']]
            if not existing_df.empty:
                existing = existing_df.iloc[0].to_dict()
        
        if existing:
            print(f"⚠ Báo cáo đã tồn tại: {work_report['reportCode']}")
            
            if auto_update:
                should_update = True
            else:
                choice = input("  Bạn có muốn cập nhật? (y/n): ")
                should_update = choice.lower() == 'y'
            
            if should_update:
                # Update báo cáo
                work_report['version'] = int(existing.get('version', 1)) + 1
                work_report['updatedAt'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                # Update trong DataFrame
                idx = df[df['reportCode'] == work_report['reportCode']].index[0]
                for key, value in work_report.items():
                    if key in df.columns:
                        df.at[idx, key] = value
                
                # Update tasks
                _update_tasks(spreadsheet, work_report)
                
                # Update reviews
                if 'reviews' in work_report:
                    _update_reviews(spreadsheet, work_report)
                
                # Update sheet
                set_with_dataframe(worksheet, df)
                
                print(f"✓ Đã cập nhật báo cáo: {work_report['reportCode']}")
                return True
            else:
                return False
        else:
            # Thêm báo cáo mới
            work_report['createdAt'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            work_report['updatedAt'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            if 'version' not in work_report:
                work_report['version'] = 1
            
            # Extract report info (không thêm tasks và reviews)
            report_info = {
                'reportCode': work_report['reportCode'],
                'employeeCode': work_report['employeeCode'],
                'employeeName': work_report.get('employeeName', ''),
                'departmentCode': work_report.get('departmentCode', ''),
                'reportPeriodYear': work_report['reportPeriod']['year'],
                'reportPeriodMonth': work_report['reportPeriod']['month'],
                'reportPeriodStartDate': work_report['reportPeriod']['startDate'],
                'reportPeriodEndDate': work_report['reportPeriod']['endDate'],
                'status': work_report.get('status', DEFAULT_REPORT_STATUS),
                'version': work_report['version'],
                'createdAt': work_report['createdAt'],
                'updatedAt': work_report['updatedAt']
            }
            
            # Thêm vào DataFrame
            new_row = pd.DataFrame([report_info])
            df = pd.concat([df, new_row], ignore_index=True)
            set_with_dataframe(worksheet, df)
            # Thêm tasks
            _insert_tasks(spreadsheet, work_report)
            
            # Thêm reviews
            if 'reviews' in work_report:
                _insert_reviews(spreadsheet, work_report)
            
            print(f"✓ Đã import báo cáo: {work_report['reportCode']}")
            return True
            
    except Exception as e:
        print(f"✗ Lỗi import báo cáo: {e}")
        import traceback
        traceback.print_exc()
        return False


def _insert_tasks(spreadsheet, work_report: Dict):
    """Insert tasks vào Google Sheets"""
    report_code = work_report['reportCode']
    
    # Insert actual tasks
    if 'actualWork' in work_report:
        actual_tasks = []
        
        # Functional tasks
        for task in work_report['actualWork'].get('functionalTasks', []):
            task_data = _prepare_task_data(task, report_code, 'functional')
            actual_tasks.append(task_data)
        
        # Project tasks
        for task in work_report['actualWork'].get('projectTasks', []):
            task_data = _prepare_task_data(task, report_code, 'project')
            actual_tasks.append(task_data)
        
        if actual_tasks:
            worksheet = spreadsheet.worksheet(SHEET_TASKS_ACTUAL)
            df = get_as_dataframe(worksheet, evaluate_formulas=True)
            df = df.dropna(how='all')
            
            new_tasks = pd.DataFrame(actual_tasks)
            df = pd.concat([df, new_tasks], ignore_index=True)
            set_with_dataframe(worksheet, df)
            print(new_tasks.columns.to_list())

    # Insert planned tasks
    if 'plannedWork' in work_report:
        planned_tasks = []
        
        # Functional tasks
        for task in work_report['plannedWork'].get('functionalTasks', []):
            task_data = _prepare_task_data(task, report_code, 'functional', is_planned=True)
            planned_tasks.append(task_data)
        
        # Project tasks
        for task in work_report['plannedWork'].get('projectTasks', []):
            task_data = _prepare_task_data(task, report_code, 'project', is_planned=True)
            planned_tasks.append(task_data)
        
        if planned_tasks:
            worksheet = spreadsheet.worksheet(SHEET_TASKS_PLANNED)
            df = get_as_dataframe(worksheet, evaluate_formulas=True)
            df = df.dropna(how='all')
            
            new_tasks = pd.DataFrame(planned_tasks)
            df = pd.concat([df, new_tasks], ignore_index=True)
            set_with_dataframe(worksheet, df)


def _update_tasks(spreadsheet, work_report: Dict):
    """Update tasks - xóa cũ và insert mới"""
    report_code = work_report['reportCode']
    
    print(f"  → Xóa tasks cũ cho report: {report_code}")
    
    # Delete old actual tasks
    worksheet = spreadsheet.worksheet(SHEET_TASKS_ACTUAL)
    df = get_as_dataframe(worksheet, evaluate_formulas=True)
    df = df.dropna(how='all')
    
    if not df.empty and 'reportCode' in df.columns:
        before_count = len(df)
        df = df[df['reportCode'] != report_code]
        after_count = len(df)
        deleted = before_count - after_count
        print(f"  → Đã xóa {deleted} actual tasks")
        
        # Clear entire sheet first
        worksheet.clear()
        # Write back the cleaned data (or just headers if empty)
        if not df.empty:
            set_with_dataframe(worksheet, df, include_index=False, include_column_header=True)
        else:
            # Restore headers if all data was deleted
            headers = ['taskId', 'reportCode', 'stt', 'taskName', 'taskType', 'category',
                      'frequency', 'startDate', 'endDate', 'result', 'description', 'solution',
                      'level', 'parentTaskId', 'hasSubtasks', 'subtaskCount', 'createdAt']
            worksheet.append_row(headers)
    
    # Delete old planned tasks
    worksheet = spreadsheet.worksheet(SHEET_TASKS_PLANNED)
    df = get_as_dataframe(worksheet, evaluate_formulas=True)
    df = df.dropna(how='all')
    
    if not df.empty and 'reportCode' in df.columns:
        before_count = len(df)
        df = df[df['reportCode'] != report_code]
        after_count = len(df)
        deleted = before_count - after_count
        print(f"  → Đã xóa {deleted} planned tasks")
        
        # Clear entire sheet first
        worksheet.clear()
        # Write back the cleaned data (or just headers if empty)
        if not df.empty:
            set_with_dataframe(worksheet, df, include_index=False, include_column_header=True)
        else:
            # Restore headers if all data was deleted
            headers = ['taskId', 'reportCode', 'stt', 'taskName', 'taskType', 'category',
                      'frequency', 'startDate', 'endDate', 'description', 'solution', 'cost', 'costUnit',
                      'level', 'parentTaskId', 'hasSubtasks', 'subtaskCount', 'createdAt']
            worksheet.append_row(headers)
    
    print(f"  → Thêm tasks mới...")
    # Insert new tasks
    _insert_tasks(spreadsheet, work_report)


def _prepare_task_data(task: Dict, report_code: str, category: str, is_planned: bool = False) -> Dict:
    """Chuẩn bị dữ liệu task để insert vào sheet"""
    # Convert children array to comma-separated string for storage
    # children_str = ','.join(task.get('children', [])) if task.get('children') else ''
    
    task_data = {
        'taskId': task.get('taskId', str(uuid.uuid4())),
        'reportCode': report_code,
        # Prefix with apostrophe to force Google Sheets to treat as text
        'stt': "'" + str(task.get('stt', '')),
        'taskName': task.get('taskName', ''),
        'taskType': task.get('taskType', ''),
        'category': category,
        'frequency': task.get('frequency', ''),
        'startDate': task.get('startDate', ''),
        'endDate': task.get('endDate', ''),
        'result': task.get('result', ''),
        'description': task.get('description', ''),
        # 'solution': task.get('solution', ''),
        # 'notes': task.get('notes', ''),
        'level': task.get('level', 0),
        'parentTaskId': task.get('parentTaskId', ''),
        'hasSubtasks': task.get('hasSubtasks', False),
        'subtaskCount': task.get('subtaskCount', 0),
        # 'children': children_str,
        'createdAt': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    if is_planned:
        # For planned tasks
        task_data['estimatedCost'] = task.get('estimatedCost', 0)
        task_data['costUnit'] = task.get('costUnit', 'VND')
    # else:
        # For actual tasks
        # task_data['evaluation'] = task.get('evaluation', '')
        # task_data['actualStartDate'] = task.get('actualStartDate', '')
        # task_data['actualEndDate'] = task.get('actualEndDate', '')
        # task_data['completionRate'] = task.get('completionRate', 0)
    
    return task_data


def _insert_reviews(spreadsheet, work_report: Dict):
    """Insert reviews vào Google Sheets"""
    if 'reviews' not in work_report:
        return
    
    reviews = work_report['reviews']
    review_data = {
        'reportCode': work_report['reportCode'],
        'dailyWorkReview': reviews.get('dailyWork', ''),
        'professionalReview': reviews.get('professional', ''),
        'createdAt': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    worksheet = spreadsheet.worksheet(SHEET_REVIEWS)
    df = get_as_dataframe(worksheet, evaluate_formulas=True)
    df = df.dropna(how='all')
    
    new_row = pd.DataFrame([review_data])
    df = pd.concat([df, new_row], ignore_index=True)
    set_with_dataframe(worksheet, df)


def _update_reviews(spreadsheet, work_report: Dict):
    """Update reviews"""
    report_code = work_report['reportCode']
    
    worksheet = spreadsheet.worksheet(SHEET_REVIEWS)
    df = get_as_dataframe(worksheet, evaluate_formulas=True)
    df = df.dropna(how='all')
    
    if not df.empty and 'reportCode' in df.columns:
        df = df[df['reportCode'] != report_code]
    
    set_with_dataframe(worksheet, df)
    _insert_reviews(spreadsheet, work_report)


def get_work_report_by_code(spreadsheet, report_code: str) -> Optional[Dict]:
    """
    Lấy báo cáo theo mã
    
    Args:
        spreadsheet: gspread Spreadsheet object
        report_code: Mã báo cáo
        
    Returns:
        Dict report hoặc None
    """
    try:
        worksheet = spreadsheet.worksheet(SHEET_WORK_REPORTS)
        df = get_as_dataframe(worksheet, evaluate_formulas=True)
        df = df.dropna(how='all')
        
        if df.empty or 'reportCode' not in df.columns:
            return None
            
        result = df[df['reportCode'] == report_code]
        if result.empty:
            return None
            
        return result.iloc[0].to_dict()
    except Exception as e:
        print(f"✗ Lỗi lấy báo cáo: {e}")
        return None


def get_reports_by_employee(spreadsheet, employee_code: str, year: int = None, month: int = None) -> List[Dict]:
    """
    Lấy danh sách báo cáo của nhân viên
    
    Args:
        spreadsheet: gspread Spreadsheet object
        employee_code: Mã nhân viên
        year: Năm (optional)
        month: Tháng (optional)
        
    Returns:
        List các báo cáo
    """
    try:
        worksheet = spreadsheet.worksheet(SHEET_WORK_REPORTS)
        df = get_as_dataframe(worksheet, evaluate_formulas=True)
        df = df.dropna(how='all')
        
        if df.empty or 'employeeCode' not in df.columns:
            return []
        
        # Filter by employee
        results = df[df['employeeCode'] == employee_code]
        
        # Filter by year
        if year and 'reportPeriodYear' in df.columns:
            results = results[results['reportPeriodYear'] == year]
        
        # Filter by month
        if month and 'reportPeriodMonth' in df.columns:
            results = results[results['reportPeriodMonth'] == month]
        
        # Sort by date
        if not results.empty and 'reportPeriodStartDate' in results.columns:
            results = results.sort_values('reportPeriodStartDate', ascending=False)
        
        return results.to_dict('records')
    except Exception as e:
        print(f"✗ Lỗi lấy báo cáo theo nhân viên: {e}")
        return []


def get_reports_by_department(spreadsheet, department_code: str, year: int = None, month: int = None) -> List[Dict]:
    """
    Lấy danh sách báo cáo của phòng ban
    
    Args:
        spreadsheet: gspread Spreadsheet object
        department_code: Mã phòng ban
        year: Năm (optional)
        month: Tháng (optional)
        
    Returns:
        List các báo cáo
    """
    try:
        worksheet = spreadsheet.worksheet(SHEET_WORK_REPORTS)
        df = get_as_dataframe(worksheet, evaluate_formulas=True)
        df = df.dropna(how='all')
        
        if df.empty or 'departmentCode' not in df.columns:
            return []
        
        # Filter by department
        results = df[df['departmentCode'] == department_code]
        
        # Filter by year
        if year and 'reportPeriodYear' in df.columns:
            results = results[results['reportPeriodYear'] == year]
        
        # Filter by month
        if month and 'reportPeriodMonth' in df.columns:
            results = results[results['reportPeriodMonth'] == month]
        
        return results.to_dict('records')
    except Exception as e:
        print(f"✗ Lỗi lấy báo cáo theo phòng ban: {e}")
        return []