"""
Google Sheets Client

Manages connection and basic operations with Google Sheets
"""

import re
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from gspread_dataframe import get_as_dataframe, set_with_dataframe
from typing import Optional, List, Dict, Any

from config import Settings
from config.constants import SheetName, COLUMN_MAPPINGS
from utils import ConnectionError, get_logger
from utils.decorators import retry, rate_limit
from utils.string_helper import string_escaping
logger = get_logger(__name__)


class GoogleSheetsClient:
    """Google Sheets API client"""
    
    def __init__(self, settings: Optional[Settings] = None):
        """
        Initialize client
        
        Args:
            settings: Settings object (creates new if None)
        """
        self.settings = settings or Settings()
        self.client: Optional[gspread.Client] = None
        self.spreadsheet: Optional[gspread.Spreadsheet] = None
        self._connect()
    
    @retry(max_attempts=3, delay=2, backoff=2)
    def _connect(self) -> None:
        """
        Connect to Google Sheets
        
        Raises:
            ConnectionError: If connection fails
        """
        try:
            credentials_path = self.settings.get_credentials_path()
            
            # Define scope
            scope = [
                'https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive'
            ]
            
            # Authenticate
            creds = Credentials.from_service_account_file(
                str(credentials_path),
                scopes=scope
            )
            self.client = gspread.authorize(creds)
            
            # Open spreadsheet
            if self.settings.GOOGLE_SHEETS_SPREADSHEET_ID:
                self.spreadsheet = self.client.open_by_key(
                    self.settings.GOOGLE_SHEETS_SPREADSHEET_ID
                )
            else:
                self.spreadsheet = self.client.open(
                    self.settings.GOOGLE_SHEETS_SPREADSHEET_NAME
                )
            
            logger.info(f"Connected to Google Sheets: {self.spreadsheet.title}")
            
            # Initialize sheets if needed
            self._initialize_sheets()
            
        except FileNotFoundError as e:
            raise ConnectionError(
                f"Credentials file not found: {credentials_path}"
            ) from e
        except Exception as e:
            raise ConnectionError(f"Failed to connect to Google Sheets: {e}") from e
    
    def _initialize_sheets(self) -> None:
        """Initialize required sheets if they don't exist"""
        existing_sheets = {sheet.title for sheet in self.spreadsheet.worksheets()}
        
        for sheet_name in SheetName:
            sheet_name_str = sheet_name.value
            
            if sheet_name_str not in existing_sheets:
                logger.info(f"Creating sheet: {sheet_name_str}")
                headers = COLUMN_MAPPINGS[sheet_name_str]
                
                # Create worksheet
                worksheet = self.spreadsheet.add_worksheet(
                    title=sheet_name_str,
                    rows=1000,
                    cols=len(headers)
                )
                
                # Set headers
                worksheet.update('A1', [headers])
                
                # Format header row
                worksheet.format('A1:Z1', {
                    "backgroundColor": {"red": 0.2, "green": 0.6, "blue": 0.9},
                    "textFormat": {
                        "bold": True,
                        "foregroundColor": {"red": 1, "green": 1, "blue": 1}
                    }
                })
    
    @rate_limit(calls_per_period=50, period=60)
    def get_worksheet(self, sheet_name: str) -> gspread.Worksheet:
        """
        Get worksheet by name
        
        Args:
            sheet_name: Name of sheet
            
        Returns:
            Worksheet object
            
        Raises:
            ConnectionError: If sheet not found
        """
        try:
            return self.spreadsheet.worksheet(sheet_name)
        except gspread.WorksheetNotFound:
            raise ConnectionError(f"Sheet not found: {sheet_name}")
    
    @rate_limit(calls_per_period=50, period=60)
    def read_sheet(self, sheet_name: str, 
                   use_header: bool = True) -> pd.DataFrame:
        """
        Read sheet data as DataFrame
        
        Args:
            sheet_name: Name of sheet
            use_header: Whether first row is header
            
        Returns:
            DataFrame with sheet data
        """
        try:
            worksheet = self.get_worksheet(sheet_name)
            df = get_as_dataframe(worksheet, header=0 if use_header else None)
            
            # Remove completely empty rows
            df = df.dropna(how='all')
            
            # Remove unnamed columns
            df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
            
            logger.debug(f"Read {len(df)} rows from {sheet_name}")
            return df
            
        except Exception as e:
            logger.error(f"Failed to read sheet {sheet_name}: {e}")
            raise
    
    @rate_limit(calls_per_period=30, period=60)
    def write_sheet(self, sheet_name: str, df: pd.DataFrame,
                    append: bool = True) -> None:
        """
        Append DataFrame to sheet
        
        Args:
            sheet_name: Name of sheet
            df: DataFrame to write
            append: Whether to append (default: True, parameter kept for backward compatibility)
        """
        try:
            worksheet = self.get_worksheet(sheet_name)
            
            # Ensure STT column is treated as string to preserve leading zeros and trailing zeros
            df_copy = df.copy()
            stt_col_index = None
            if 'stt' in df_copy.columns:
                df_copy['stt'] = df_copy['stt'].astype(str)
                stt_col_index = df_copy.columns.get_loc('stt')
            
            # Get the last row with data
            existing_values = worksheet.get_all_values()
            next_row = len(existing_values) + 1
            
            # If sheet is empty, write with header
            if next_row == 1:
                set_with_dataframe(worksheet, df_copy, include_index=False, include_column_header=True, row=1)
            else:
                # Append without header
                set_with_dataframe(worksheet, df_copy, include_index=False, include_column_header=False, row=next_row)
            
            # Format STT column as TEXT to preserve values like "3.10"
            if stt_col_index is not None:
                self._format_column_as_text(worksheet, stt_col_index)
            
            logger.info(f"Appended {len(df)} rows to {sheet_name}")
            
        except Exception as e:
            logger.error(f"Failed to write to sheet {sheet_name}: {e}")
            raise
    
    @rate_limit(calls_per_period=30, period=60)
    def append_rows(self, sheet_name: str, rows: List[List[Any]]) -> None:
        """
        Append rows to sheet
        
        Args:
            sheet_name: Name of sheet
            rows: List of row data
        """
        try:
            worksheet = self.get_worksheet(sheet_name)
            worksheet.append_rows(rows)
            
            logger.debug(f"Appended {len(rows)} rows to {sheet_name}")
            
        except Exception as e:
            logger.error(f"Failed to append rows to {sheet_name}: {e}")
            raise
    
    @rate_limit(calls_per_period=50, period=60)
    def find_rows(self, sheet_name: str, 
                  column: str, value: Any) -> pd.DataFrame:
        """
        Find rows where column equals value
        
        Args:
            sheet_name: Name of sheet
            column: Column name
            value: Value to match
            
        Returns:
            DataFrame with matching rows
        """
        df = self.read_sheet(sheet_name)
        
        if df.empty:
            return pd.DataFrame()
        
        if column not in df.columns:
            logger.warning(f"Column '{column}' not found in {sheet_name}")
            return pd.DataFrame()
        
        # Convert both to string for comparison to handle type mismatches
        df[column] = df[column].astype(str)
        value_str = str(value)
        
        result = df[df[column] == value_str]
        logger.debug(f"Found {len(result)} rows where {column}={value}")
        
        return result
    
    @rate_limit(calls_per_period=30, period=60)
    def update_rows(self, sheet_name: str, 
                    condition_column: str, condition_value: Any,
                    updates: Dict[str, Any]) -> int:
        """
        Update rows matching condition
        
        Args:
            sheet_name: Name of sheet
            condition_column: Column to match
            condition_value: Value to match
            updates: Dictionary of column: value updates
            
        Returns:
            Number of rows updated
        """
        try:
            df = self.read_sheet(sheet_name)
            
            if df.empty:
                logger.debug(f"Sheet {sheet_name} is empty")
                return 0
            
            if condition_column not in df.columns:
                logger.warning(f"Column '{condition_column}' not found")
                return 0
            
            # Convert both to string for comparison to handle type mismatches
            df[condition_column] = df[condition_column].astype(str)
            condition_value_str = str(condition_value)
            
            # Find matching rows
            mask = df[condition_column] == condition_value_str
            count = mask.sum()
            
            if count == 0:
                logger.debug(f"No rows found where {condition_column}={condition_value}")
                return 0
            
            # Apply updates
            for col, val in updates.items():
                if col in df.columns:
                    df.loc[mask, col] = val
            
            # Replace entire sheet with updated data
            worksheet = self.get_worksheet(sheet_name)
            worksheet.clear()
            set_with_dataframe(worksheet, df, include_index=False, include_column_header=True)
            
            logger.info(f"Updated {count} rows in {sheet_name}")
            return count
            
        except Exception as e:
            logger.error(f"Failed to update rows in {sheet_name}: {e}")
            raise
    
    @rate_limit(calls_per_period=30, period=60)
    def delete_rows(self, sheet_name: str,
                    column: str, value: Any) -> int:
        """
        Delete rows where column equals value
        
        Args:
            sheet_name: Name of sheet
            column: Column name
            value: Value to match
            
        Returns:
            Number of rows deleted
        """
        try:
            worksheet = self.get_worksheet(sheet_name)
            
            # Get all values to find matching rows
            all_values = worksheet.get_all_values()
            
            if not all_values:
                logger.debug(f"No data in sheet {sheet_name}")
                return 0
            
            # Get header row and find column index
            headers = all_values[0]
            try:
                col_index = headers.index(column)
            except ValueError:
                logger.warning(f"Column '{column}' not found in headers")
                return 0
            
            # Find row indices to delete (in reverse order to avoid index shifting)
            rows_to_delete = []
            for row_idx, row in enumerate(all_values[1:], start=2):  # Start from 2 (skip header)
                if col_index < len(row) and row[col_index] == str(value):
                    rows_to_delete.append(row_idx)
            
            count = len(rows_to_delete)
            
            if count == 0:
                logger.debug(f"No rows found where {column}={value}")
                return 0
            
            # Delete rows in reverse order to maintain correct indices
            for row_idx in reversed(rows_to_delete):
                worksheet.delete_rows(row_idx)
            
            logger.info(f"Deleted {count} rows from {sheet_name}")
            return count
            
        except Exception as e:
            logger.error(f"Failed to delete rows from {sheet_name}: {e}")
            raise
    
    def _format_column_as_text(self, worksheet, col_index: int) -> None:
        """
        Format a column as TEXT to preserve values like "3.10"
        
        Args:
            worksheet: The worksheet object
            col_index: Zero-based column index
        """
        try:
            # Format the entire column as TEXT
            worksheet.format(
                f"{chr(65 + col_index)}:{chr(65 + col_index)}",
                {
                    "numberFormat": {
                        "type": "TEXT"
                    }
                }
            )
            logger.debug(f"Formatted column {col_index} as TEXT")
        except Exception as e:
            logger.warning(f"Could not format column as TEXT: {e}")
    
    def test_connection(self) -> bool:
        """
        Test if connection is active
        
        Returns:
            True if connected
        """
        try:
            _ = self.spreadsheet.title
            return True
        except:
            return False
