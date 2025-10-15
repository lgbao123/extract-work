import datetime
import pandas as pd
def flatten_multiindex_columns(df):
    """
    Combine multi-level column headers into single level with proper formatting
    
    Args:
        df: DataFrame with multi-level columns
        
    Returns:
        DataFrame with flattened column names
    """
    if isinstance(df.columns, pd.MultiIndex):
        # Combine the two levels with ' - ' separator, clean up empty values
        new_columns = []
        for col in df.columns:
            # Get level 0 and level 1, convert to string and strip whitespace
            level0 = str(col[0]).strip() if "Unnamed" not in str(col[0]) else ""
            level1 = str(col[1]).strip() if "Unnamed" not in str(col[1]) else ""
            
            # Combine non-empty levels
            if level0 and level1:
                combined = level1
            elif level0:
                combined = level0
            elif level1:
                combined = level1
            else:
                combined = "Unnamed"
            new_columns.append(combined)
        df.columns = new_columns
    return df


# Convert datetime objects to ISO format strings for JSON serialization
def convert_datetime(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, dict):
        return {k: convert_datetime(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [convert_datetime(i) for i in obj]
    return obj