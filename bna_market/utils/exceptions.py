"""
Custom exception classes for BNA Market application

DEPRECATED: Use bna_market.core.exceptions instead.
This file is kept for backwards compatibility but all exceptions
should be imported from bna_market.core.exceptions.
"""

# Re-export from core.exceptions for backwards compatibility
from bna_market.core.exceptions import (
    BNAMarketError,
    PipelineError,
    APIError,
    DataValidationError,
    DatabaseError,
)

__all__ = [
    "BNAMarketError",
    "PipelineError",
    "APIError",
    "DataValidationError",
    "DatabaseError",
]
