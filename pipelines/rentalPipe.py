"""
Rental property pipeline for BNA Market

Fetches rental property listings from Zillow API with unit parsing.
"""

import pandas as pd
import json
import ast
import re
from dotenv import load_dotenv
import os
from pipelines.zillow_base import fetch_zillow_listings
from config.settings import ZILLOW_CONFIG
from utils.logger import setup_logger

load_dotenv()
logger = setup_logger("rental_pipeline")


def parse_units(x):
    """
    Parse units field from string representation to list

    Args:
        x: Units data (could be list, string, or other)

    Returns:
        Parsed list or None if parsing fails
    """
    if isinstance(x, list):
        return x
    if not isinstance(x, str):
        return None

    # Try literal_eval first
    try:
        return ast.literal_eval(x)
    except (ValueError, SyntaxError):
        pass

    # Try JSON parsing with boolean replacements
    try:
        s = x.replace("False", "false").replace("True", "true")
        s = re.sub(r"'", '"', s)
        return json.loads(s)
    except (ValueError, json.JSONDecodeError):
        return None


def rentalPipe01() -> pd.DataFrame:
    """
    Fetch rental property listings from Zillow API

    Returns:
        DataFrame with rental property listings, with units exploded if present

    Raises:
        ValueError: If RAPID_API_KEY is not found in environment
    """
    api_key = os.getenv("RAPID_API_KEY")
    if not api_key:
        raise ValueError("RAPID_API_KEY not found in environment")

    df = fetch_zillow_listings(
        status_type="ForRent",
        config=ZILLOW_CONFIG["rentals"],
        api_key=api_key,
        max_pages=ZILLOW_CONFIG["rentals"]["max_pages"],
        page_delay=ZILLOW_CONFIG["rentals"]["page_delay"],
    )

    # Only parse units if the column exists and DataFrame is not empty
    if not df.empty and "units" in df.columns:
        logger.info("Parsing units column for multi-unit properties")
        df["parsed"] = df["units"].apply(parse_units)
        df = df.explode("parsed")

        # Extract unit fields and add as separate columns
        new_cols = df["parsed"].apply(pd.Series).add_suffix("_unit")
        df = pd.concat([df.drop(columns=["parsed"]), new_cols], axis=1)
        logger.info(f"Units parsed and exploded into {len(new_cols.columns)} unit-specific columns")

    return df


if __name__ == "__main__":
    # Test the pipeline
    df = rentalPipe01()
    print(f"\nCollected {len(df)} rental properties")
    if not df.empty:
        print(f"DataFrame shape: {df.shape}")
        print(f"Columns: {list(df.columns)[:15]}...")  # Show first 15 columns
