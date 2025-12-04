"""
BNA Market - Nashville Real Estate Market Analytics

A data analytics platform for Nashville real estate market with:
- Property data collection from Zillow (for-sale & rentals)
- Economic indicators from FRED
- SQLite database storage with deduplication
- Flask dashboard with Plotly visualizations
- SaaS features (authentication, billing, API)
"""

__version__ = "2.0.0"

from bna_market.services import ETLService, run_etl
from bna_market.core.config import settings, DATABASE_CONFIG, ZILLOW_CONFIG, FRED_CONFIG

__all__ = [
    "ETLService",
    "run_etl",
    "settings",
    "DATABASE_CONFIG",
    "ZILLOW_CONFIG",
    "FRED_CONFIG",
]
