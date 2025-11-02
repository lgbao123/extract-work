import re
import pandas as pd
from datetime import datetime,date
def clean_frequency(val):
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