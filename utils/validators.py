from typing import Dict, List


def validate_employee_data(employee_data: Dict) -> tuple[bool, str]:
    """
    Validate dữ liệu nhân viên
    
    Args:
        employee_data: Dict thông tin nhân viên
        
    Returns:
        (is_valid, error_message)
    """
    required_fields = ["employeeCode", "fullName", "email", "department"]
    
    for field in required_fields:
        if field not in employee_data or not employee_data[field]:
            return False, f"Thiếu field bắt buộc: {field}"
    
    # Validate email format
    email = employee_data["email"]
    if "@" not in email or "." not in email:
        return False, f"Email không hợp lệ: {email}"
    
    return True, ""


def validate_work_report(work_report: Dict) -> tuple[bool, str]:
    """
    Validate dữ liệu báo cáo
    
    Args:
        work_report: Dict báo cáo công việc
        
    Returns:
        (is_valid, error_message)
    """
    required_fields = ["reportCode", "employeeCode", "reportPeriod"]
    
    for field in required_fields:
        if field not in work_report or not work_report[field]:
            return False, f"Thiếu field bắt buộc: {field}"
    
    # Validate report period
    period = work_report.get("reportPeriod", {})
    if not period.get("startDate") or not period.get("endDate"):
        return False, "Kỳ báo cáo không hợp lệ"
    
    return True, ""


def validate_tasks(tasks: List[Dict]) -> tuple[bool, str]:
    """
    Validate danh sách tasks
    
    Args:
        tasks: List các task
        
    Returns:
        (is_valid, error_message)
    """
    if not tasks:
        return True, ""  # Empty is valid
    
    task_ids = set()
    for task in tasks:
        # Check required fields
        if not task.get("taskId") or not task.get("taskName"):
            return False, "Task thiếu taskId hoặc taskName"
        
        # Check duplicate taskId
        if task["taskId"] in task_ids:
            return False, f"Duplicate taskId: {task['taskId']}"
        task_ids.add(task["taskId"])
        
        # Validate parent-child relationship
        if task.get("parentTaskId") and task["parentTaskId"] not in task_ids:
            # Parent phải xuất hiện trước child
            pass  # Warning only, not error
    
    return True, ""