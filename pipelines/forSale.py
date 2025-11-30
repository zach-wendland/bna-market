"""
For-sale property pipeline for BNA Market

Fetches for-sale property listings from Zillow API.
"""
from dotenv import load_dotenv
import os
import pandas as pd
from pipelines.zillow_base import fetch_zillow_listings
from config.settings import ZILLOW_CONFIG

load_dotenv()


def forSalePipe01() -> pd.DataFrame:
    """
    Fetch for-sale property listings from Zillow API

    Returns:
        DataFrame with for-sale property listings

    Raises:
        ValueError: If RAPID_API_KEY is not found in environment
    """
    api_key = os.getenv("RAPID_API_KEY")
    if not api_key:
        raise ValueError("RAPID_API_KEY not found in environment")

    return fetch_zillow_listings(
        status_type='ForSale',
        config=ZILLOW_CONFIG['for_sale'],
        api_key=api_key,
        max_pages=ZILLOW_CONFIG['for_sale']['max_pages'],
        page_delay=ZILLOW_CONFIG['for_sale']['page_delay']
    )


if __name__ == "__main__":
    # Test the pipeline
    df = forSalePipe01()
    print(f"\nCollected {len(df)} for-sale properties")
    if not df.empty:
        print(f"DataFrame shape: {df.shape}")
        print(f"Columns: {list(df.columns)[:10]}...")  # Show first 10 columns
