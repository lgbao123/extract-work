import re
from datetime import datetime
from typing import Dict, Optional, Any, Tuple
import pandas as pd
from config.settings import DATE_FORMATS


def parse_stt(stt: str) -> Tuple[int, Optional[str]]:
    """
    Parse STT để xác định level và parent
    
    Args:
        stt: STT dạng "1", "1.1", "1.1.1"
        
    Returns:
        (level, parent_stt)
        
    Examples:
        >>> parse_stt("1")
        (0, None)
        >>> parse_stt("1.1")
        (1, "1")
        >>> parse_stt("2.1.3")
        (2, "2.1")
    """
    if pd.isna(stt) or str(stt).strip() == "":
        return (0, None)
    
    stt_str = str(stt).strip()
    parts = stt_str.split(".")
    level = len(parts) - 1
    
    if level == 0:
        parent_stt = None
    else:
        parent_stt = ".".join(parts[:-1])
    
    return (level, parent_stt)


def parse_date(date_value: Any) -> Optional[datetime]:
    """
    Parse date từ nhiều format khác nhau
    
    Args:
        date_value: Giá trị date (string hoặc datetime)
        
    Returns:
        datetime object hoặc None
        
    Examples:
        >>> parse_date("21/08/2025")
        datetime(2025, 8, 21)
        >>> parse_date("2025-08-21")
        datetime(2025, 8, 21)
    """
    if pd.isna(date_value):
        return None
    
    if isinstance(date_value, datetime):
        return date_value
    
    date_str = str(date_value).strip()
    
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    return None


def extract_report_period(title: str) -> Dict:
    """
    Extract thông tin kỳ báo cáo từ title
    
    Args:
        title: Title chứa thông tin kỳ báo cáo
        VD: "Từ ngày 20/7/2025 đến hết ngày 20/8/2025"
        
    Returns:
        Dict chứa startDate, endDate, year, month
        
    Examples:
        >>> period = extract_report_period("Từ ngày 20/7/2025 đến hết ngày 20/8/2025")
        >>> period["year"]
        2025
        >>> period["month"]
        7
    """
    # Pattern để extract date
    pattern = r"(\\d{1,2})/(\\d{1,2})/(\\d{4})"
    matches = re.findall(pattern, title)
    
    if len(matches) >= 2:
        # Start date
        start_day, start_month, start_year = matches[0]
        start_date = datetime(int(start_year), int(start_month), int(start_day))
        
        # End date
        end_day, end_month, end_year = matches[1]
        end_date = datetime(int(end_year), int(end_month), int(end_day))
        
        return {
            "type": "monthly",
            "startDate": start_date,
            "endDate": end_date,
            "year": int(start_year),
            "month": int(start_month)
        }
    
    # Default: tháng hiện tại
    now = datetime.now()
    return {
        "type": "monthly",
        "startDate": datetime(now.year, now.month, 20),
        "endDate": datetime(now.year, now.month + 1 if now.month < 12 else 1, 20),
        "year": now.year,
        "month": now.month
    }


def parse_cost(cost_str: str) -> float:
    """
    Parse chi phí từ string sang float
    
    Args:
        cost_str: String chi phí (có thể có dấu phẩy, chấm)
        
    Returns:
        Float value
        
    Examples:
        >>> parse_cost("50,000,000")
        50000000.0
        >>> parse_cost("50.000.000")
        50000000.0
    """
    try:
        clean_str = str(cost_str).strip().replace(',', '').replace('.', '')
        return float(clean_str)
    except:
        return 0.0