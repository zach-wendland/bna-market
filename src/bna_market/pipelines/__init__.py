"""
Data collection pipelines for BNA Market

Provides functions to fetch data from external APIs:
- Zillow (for-sale and rental properties)
- FRED (economic indicators)
"""

from bna_market.pipelines.for_sale import fetch_for_sale_properties
from bna_market.pipelines.rental import fetch_rental_properties, parse_units
from bna_market.pipelines.fred_metrics import fetch_fred_metrics

__all__ = [
    "fetch_for_sale_properties",
    "fetch_rental_properties",
    "fetch_fred_metrics",
    "parse_units",
]
