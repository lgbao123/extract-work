"""
Base Repository

Abstract CRUD operations for all repositories
"""

from abc import ABC, abstractmethod
from typing import TypeVar, Generic, List, Optional, Dict, Any
import pandas as pd
from datetime import datetime

from .google_sheets_client import GoogleSheetsClient
from utils import RepositoryError, get_logger

logger = get_logger(__name__)

# Type variable for model
T = TypeVar('T')


class BaseRepository(ABC, Generic[T]):
    """Abstract base repository with CRUD operations"""
    
    def __init__(self, client: GoogleSheetsClient, sheet_name: str):
        """
        Initialize repository
        
        Args:
            client: Google Sheets client
            sheet_name: Name of sheet for this repository
        """
        self.client = client
        self.sheet_name = sheet_name
    
    @abstractmethod
    def model_to_dict(self, model: T) -> Dict[str, Any]:
        """
        Convert model to dictionary for storage
        
        Args:
            model: Model instance
            
        Returns:
            Dictionary
        """
        pass
    
    @abstractmethod
    def dict_to_model(self, data: Dict[str, Any]) -> T:
        """
        Convert dictionary to model
        
        Args:
            data: Dictionary data
            
        Returns:
            Model instance
        """
        pass
    
    @abstractmethod
    def get_id_column(self) -> str:
        """
        Get the primary key column name
        
        Returns:
            Column name
        """
        pass
    
    def create(self, model: T) -> T:
        """
        Create new record
        
        Args:
            model: Model to create
            
        Returns:
            Created model with updated timestamps
            
        Raises:
            RepositoryError: If creation fails
        """
        try:
            # Check if record already exists
            id_value = self.get_id_value(model)
            existing = self.get_by_id(id_value)
            
            if existing:
                logger.warning(f"{self.sheet_name} record already exists: {id_value}")
                return existing
            
            # Convert to dict
            data = self.model_to_dict(model)
            
            # Add timestamps
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            data['createdAt'] = now
            if 'updatedAt' in data:
                data['updatedAt'] = now
            
            # Convert to DataFrame
            df = pd.DataFrame([data])
            
            # Write to sheet
            self.client.write_sheet(self.sheet_name, df, append=True)
            
            logger.info(f"Created {self.sheet_name} record: {id_value}")
            
            # Update model with timestamps
            if hasattr(model, 'created_at'):
                model.created_at = now
            if hasattr(model, 'updated_at'):
                model.updated_at = now
            
            return model
            
        except Exception as e:
            raise RepositoryError(f"Failed to create {self.sheet_name}: {e}") from e
    
    def create_many(self, models: List[T]) -> List[T]:
        """
        Create multiple records
        
        Args:
            models: List of models to create
            
        Returns:
            List of created models
        """
        if not models:
            return []
        
        try:
            # Convert all to dicts
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            data_list = []
            
            for model in models:
                data = self.model_to_dict(model)
                data['createdAt'] = now
                if 'updatedAt' in data:
                    data['updatedAt'] = now
                data_list.append(data)
                
                # Update model
                if hasattr(model, 'created_at'):
                    model.created_at = now
                if hasattr(model, 'updated_at'):
                    model.updated_at = now
            
            # Convert to DataFrame
            df = pd.DataFrame(data_list)
            
            # Write to sheet
            self.client.write_sheet(self.sheet_name, df, append=True)
            
            logger.info(f"Created {len(models)} {self.sheet_name} records")
            
            return models
            
        except Exception as e:
            raise RepositoryError(
                f"Failed to create multiple {self.sheet_name}: {e}"
            ) from e
    
    def get_by_id(self, id_value: Any) -> Optional[T]:
        """
        Get record by ID
        
        Args:
            id_value: ID value
            
        Returns:
            Model instance or None
        """
        try:
            df = self.client.find_rows(
                self.sheet_name,
                self.get_id_column(),
                id_value
            )
            
            if df.empty:
                return None
            
            # Get first matching row
            row_dict = df.iloc[0].to_dict()
            return self.dict_to_model(row_dict)
            
        except Exception as e:
            logger.error(f"Failed to get {self.sheet_name} by ID {id_value}: {e}")
            return None
    
    def get_all(self) -> List[T]:
        """
        Get all records
        
        Returns:
            List of model instances
        """
        try:
            df = self.client.read_sheet(self.sheet_name)
            
            if df.empty:
                return []
            
            models = []
            for _, row in df.iterrows():
                try:
                    model = self.dict_to_model(row.to_dict())
                    models.append(model)
                except Exception as e:
                    logger.warning(f"Failed to parse row: {e}")
            
            return models
            
        except Exception as e:
            logger.error(f"Failed to get all {self.sheet_name}: {e}")
            return []
    
    def find_by(self, column: str, value: Any) -> List[T]:
        """
        Find records by column value
        
        Args:
            column: Column name
            value: Value to match
            
        Returns:
            List of matching models
        """
        try:
            df = self.client.find_rows(self.sheet_name, column, value)
            
            if df.empty:
                return []
            
            models = []
            for _, row in df.iterrows():
                try:
                    model = self.dict_to_model(row.to_dict())
                    models.append(model)
                except Exception as e:
                    logger.warning(f"Failed to parse row: {e}")
            
            return models
            
        except Exception as e:
            logger.error(f"Failed to find {self.sheet_name} by {column}={value}: {e}")
            return []
    
    def update(self, id_value: Any, updates: Dict[str, Any]) -> bool:
        """
        Update record
        
        Args:
            id_value: ID value
            updates: Dictionary of field updates
            
        Returns:
            True if updated successfully
        """
        try:
            # Add update timestamp
            updates['updatedAt'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Update rows
            count = self.client.update_rows(
                self.sheet_name,
                self.get_id_column(),
                id_value,
                updates
            )
            
            if count > 0:
                logger.info(f"Updated {self.sheet_name} record: {id_value}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to update {self.sheet_name} {id_value}: {e}")
            return False
    
    def delete(self, id_value: Any) -> bool:
        """
        Delete record
        
        Args:
            id_value: ID value
            
        Returns:
            True if deleted successfully
        """
        try:
            count = self.client.delete_rows(
                self.sheet_name,
                self.get_id_column(),
                id_value
            )
            
            if count > 0:
                logger.info(f"Deleted {self.sheet_name} record: {id_value}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to delete {self.sheet_name} {id_value}: {e}")
            return False
    
    def exists(self, id_value: Any) -> bool:
        """
        Check if record exists
        
        Args:
            id_value: ID value
            
        Returns:
            True if exists
        """
        return self.get_by_id(id_value) is not None
    
    def count(self) -> int:
        """
        Count total records
        
        Returns:
            Number of records
        """
        try:
            df = self.client.read_sheet(self.sheet_name)
            return len(df)
        except:
            return 0
    
    def get_id_value(self, model: T) -> Any:
        """
        Get ID value from model
        
        Args:
            model: Model instance
            
        Returns:
            ID value
        """
        id_column = self.get_id_column()
        
        # Try snake_case version
        snake_case_attr = id_column.replace('Code', '_code').replace('Id', '_id')
        
        if hasattr(model, snake_case_attr):
            return getattr(model, snake_case_attr)
        
        # Try camelCase version
        if hasattr(model, id_column):
            return getattr(model, id_column)
        
        # Try lowercase
        if hasattr(model, id_column.lower()):
            return getattr(model, id_column.lower())
        
        raise AttributeError(f"Model has no attribute {id_column}")
