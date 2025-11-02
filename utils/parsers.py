import re
from datetime import date, datetime
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
    
    
def clean_frequency(val):
    """
    Clean frequency value
    Args:
        val: frequency value (string, datetime, NaN, etc)
    Returns:
        Skips if the value is a date or null/NaN/blank
        return Cleaned frequency string hoặc empty string nếu không hợp lệ
    """
    # Skip NaN / None / empty strings
    if pd.isna(val) or str(val).strip().lower() in ['nan', 'none', '']:
        return ''
    
    # Skip if it's an actual datetime or pandas Timestamp
    if isinstance(val, (datetime,date, pd.Timestamp)):
        return ''
    
    # Convert to string and clean up whitespace/newlines
    s = str(val).strip()
    
    # Skip if the string looks like a date (e.g. 2025-09-01, 08/07/2025, 2025/09/03 00:00)
    if re.search(r'\d{1,4}[-/]\d{1,2}[-/]\d{1,4}', s):
        return ''
    return s

def parse_emty_string(s: str) -> str:
    """
    Parse empty strings và các giá trị không hợp lệ
    
    Args:
        s: Input string (có thể là None, NaN, "null", "none", etc)
        
    Returns:
        Cleaned string hoặc empty string nếu không hợp lệ
    """
    if pd.isna(s):
        return ''
    
    s_clean = str(s).strip()
    if s_clean.lower() in ['nan', 'none', 'null', '']:
        return ''
    
    return s_clean