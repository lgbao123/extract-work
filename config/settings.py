"""
Settings Module

Load and manage application settings from environment variables
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings:
    """Application settings loaded from environment variables"""
    
    # Project paths
    BASE_DIR: Path = Path(__file__).parent.parent
    INPUT_DIR: Path = BASE_DIR / "input"
    OUTPUT_DIR: Path = BASE_DIR / "output"
    LOGS_DIR: Path = BASE_DIR / "logs"
    
    # Google Sheets Configuration
    GOOGLE_SHEETS_CREDENTIALS_FILE: str = os.getenv(
        "GOOGLE_SHEETS_CREDENTIALS_FILE", 
        "credentials.json"
    )
    GOOGLE_SHEETS_SPREADSHEET_ID: Optional[str] = os.getenv(
        "GOOGLE_SHEETS_SPREADSHEET_ID"
    )
    GOOGLE_SHEETS_SPREADSHEET_NAME: str = os.getenv(
        "GOOGLE_SHEETS_SPREADSHEET_NAME", 
        "Work Report Database"
    )
    
    # Application Settings
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    AUTO_UPDATE: bool = os.getenv("AUTO_UPDATE", "False").lower() == "true"
    
    # Batch Processing
    BATCH_SIZE: int = int(os.getenv("BATCH_SIZE", "50"))
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))
    RETRY_DELAY: int = int(os.getenv("RETRY_DELAY", "5"))
    
    # Rate Limiting (Google Sheets API)
    RATE_LIMIT_CALLS: int = int(os.getenv("RATE_LIMIT_CALLS", "50"))
    RATE_LIMIT_PERIOD: int = int(os.getenv("RATE_LIMIT_PERIOD", "60"))
    
    @classmethod
    def get_credentials_path(cls) -> Path:
        """Get absolute path to credentials file"""
        creds_path = cls.BASE_DIR / cls.GOOGLE_SHEETS_CREDENTIALS_FILE
        return creds_path
    
    @classmethod
    def ensure_directories(cls) -> None:
        """Ensure required directories exist"""
        cls.INPUT_DIR.mkdir(parents=True, exist_ok=True)
        cls.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        cls.LOGS_DIR.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def validate(cls) -> tuple[bool, Optional[str]]:
        """
        Validate settings
        
        Returns:
            (is_valid, error_message)
        """
        # Check credentials file
        if not cls.get_credentials_path().exists():
            return False, f"Credentials file not found: {cls.GOOGLE_SHEETS_CREDENTIALS_FILE}"
        
        # Check spreadsheet ID or name
        if not cls.GOOGLE_SHEETS_SPREADSHEET_ID and not cls.GOOGLE_SHEETS_SPREADSHEET_NAME:
            return False, "Either GOOGLE_SHEETS_SPREADSHEET_ID or GOOGLE_SHEETS_SPREADSHEET_NAME must be set"
        
        return True, None


# Create singleton instance
settings = Settings()
