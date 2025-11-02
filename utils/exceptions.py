"""
Custom Exceptions Module

Define custom exception classes for the application
"""


class WorkReportError(Exception):
    """Base exception for work report system"""
    pass


class ValidationError(WorkReportError):
    """Raised when data validation fails"""
    pass


class ParsingError(WorkReportError):
    """Raised when parsing files fails"""
    pass


class RepositoryError(WorkReportError):
    """Raised when database/repository operations fail"""
    pass


class ConfigurationError(WorkReportError):
    """Raised when configuration is invalid"""
    pass


class ConnectionError(WorkReportError):
    """Raised when connection to external service fails"""
    pass


class GoogleSheetsError(RepositoryError):
    """Raised when Google Sheets API operations fail"""
    pass


class RateLimitError(RepositoryError):
    """Raised when API rate limit is exceeded"""
    pass


class DataNotFoundError(RepositoryError):
    """Raised when requested data is not found"""
    pass


class DuplicateDataError(RepositoryError):
    """Raised when attempting to insert duplicate data"""
    pass


class ServiceError(WorkReportError):
    """Raised when service layer operations fail"""
    pass
