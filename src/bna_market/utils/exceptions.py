"""
Custom exception classes for BNA Market application

Provides specific exception types for different error categories.
"""


class PipelineError(Exception):
    """Base exception for pipeline errors"""

    pass


class APIError(PipelineError):
    """API request/response errors"""

    pass


class DataValidationError(PipelineError):
    """Data quality/validation errors"""

    pass


class DatabaseError(PipelineError):
    """Database operation errors"""

    pass
