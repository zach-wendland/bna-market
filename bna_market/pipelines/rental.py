"""
Rental property pipeline for BNA Market

Fetches rental property listings from Zillow API with unit parsing for multi-unit properties.
"""

import ast
import json
import re
from typing import Any

import pandas as pd

from bna_market.pipelines.zillow_base import fetch_zillow_listings
from bna_market.core.config import ZILLOW_CONFIG, settings
from bna_market.utils.logger import setup_logger

logger = setup_logger("rental_pipeline")


def parse_units(x: Any) -> list[dict[str, Any]] | None:
    """
    Parse units field from string representation to list

    Handles various formats including Python literal strings and JSON.

    Args:
        x: Units data (could be list, string, or other type)

    Returns:
        Parsed list of unit dictionaries, or None if parsing fails

    Example:
        >>> parse_units("[{'beds': 2, 'price': 1800}]")
        [{'beds': 2, 'price': 1800}]
    """
    if isinstance(x, list):
        return x
    if not isinstance(x, str):
        return None

    # Try literal_eval first (for Python literal strings)
    try:
        result = ast.literal_eval(x)
        return result if isinstance(result, list) else None
    except (ValueError, SyntaxError):
        pass

    # Try JSON parsing with boolean replacements
    try:
        s = x.replace("False", "false").replace("True", "true")
        s = re.sub(r"'", '"', s)
        result = json.loads(s)
        return result if isinstance(result, list) else None
    except (ValueError, json.JSONDecodeError):
        logger.debug(f"Failed to parse units field: {str(x)[:100]}...")
        return None


def fetch_rental_properties() -> pd.DataFrame:
    """
    Fetch rental property listings from Zillow API

    Applies filters defined in ZILLOW_CONFIG for rentals:
    - Price range: $1400 - $3200/month
    - Bedrooms: 1-4
    - Bathrooms: 1-4
    - Square footage: 550-6000
    - Built after: 1979

    Returns:
        DataFrame with rental property listings
        If 'units' column exists, explodes multi-unit properties into separate rows
        with unit-specific fields suffixed with '_unit'

    Raises:
        ValueError: If RAPID_API_KEY is not found in environment

    Example:
        >>> df = fetch_rental_properties()
        >>> print(f"Fetched {len(df)} rental units")
    """
    # Import os here to check environment directly (for test compatibility)
    import os
    api_key = os.getenv("RAPID_API_KEY", "")
    if not api_key:
        raise ValueError("RAPID_API_KEY not found in environment")

    config = ZILLOW_CONFIG["rentals"]

    logger.info("Fetching rental properties from Zillow API")
    df = fetch_zillow_listings(
        status_type="ForRent",
        config=config,
        api_key=api_key,
        max_pages=config["max_pages"],
        page_delay=config["page_delay"],
    )

    # Parse and explode units if column exists and DataFrame is not empty
    if not df.empty and "units" in df.columns:
        logger.info("Parsing units column for multi-unit properties")
        df["parsed"] = df["units"].apply(parse_units)
        df = df.explode("parsed")

        # Extract unit fields and add as separate columns
        new_cols = df["parsed"].apply(pd.Series).add_suffix("_unit")
        df = pd.concat([df.drop(columns=["parsed"]), new_cols], axis=1)
        logger.info(f"Units parsed and exploded into {len(new_cols.columns)} unit-specific columns")

    logger.info(f"Fetched {len(df)} rental units")
    return df
