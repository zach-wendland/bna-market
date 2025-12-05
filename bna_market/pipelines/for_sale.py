"""
For-sale property pipeline for BNA Market

Fetches for-sale property listings from Zillow API with filtering and validation.
"""

import pandas as pd

from bna_market.pipelines.zillow_base import fetch_zillow_listings
from bna_market.core.config import ZILLOW_CONFIG, settings
from bna_market.utils.logger import setup_logger

logger = setup_logger("for_sale_pipeline")


def fetch_for_sale_properties() -> pd.DataFrame:
    """
    Fetch for-sale property listings from Zillow API

    Applies filters defined in ZILLOW_CONFIG for for-sale properties:
    - Price range: $100k - $700k
    - Bedrooms: 1-5
    - Bathrooms: 1-4
    - Square footage: 700-5000
    - Built after: 1990

    Returns:
        DataFrame with for-sale property listings

    Raises:
        ValueError: If RAPID_API_KEY is not found in environment

    Example:
        >>> df = fetch_for_sale_properties()
        >>> print(f"Fetched {len(df)} properties")
    """
    api_key = settings["rapid_api_key"]
    if not api_key:
        raise ValueError("RAPID_API_KEY not found in environment")

    config = ZILLOW_CONFIG["for_sale"]

    logger.info("Fetching for-sale properties from Zillow API")
    df = fetch_zillow_listings(
        status_type="ForSale",
        config=config,
        api_key=api_key,
        max_pages=config["max_pages"],
        page_delay=config["page_delay"],
    )

    logger.info(f"Fetched {len(df)} for-sale properties")
    return df
