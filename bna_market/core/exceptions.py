"""Custom exceptions for BNA Market application"""


class BNAMarketError(Exception):
    """Base exception for BNA Market"""

    pass


class PipelineError(BNAMarketError):
    """Raised when pipeline execution fails"""

    pass


class APIError(BNAMarketError):
    """Raised when external API call fails"""

    pass


class DataValidationError(BNAMarketError):
    """Raised when data validation fails"""

    pass


class DatabaseError(BNAMarketError):
    """Raised when database operation fails"""

    pass
