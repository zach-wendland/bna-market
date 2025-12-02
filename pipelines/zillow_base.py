"""
Shared Zillow API functionality for BNA Market pipelines

Eliminates code duplication between forSale and rental pipelines.
"""

import requests
import pandas as pd
import time
from typing import Dict
from utils.logger import setup_logger
from utils.retry import retry_with_backoff
from utils.validators import validate_zillow_dataframe
from config.settings import NASHVILLE_POLYGON

logger = setup_logger("zillow_pipeline")


@retry_with_backoff(max_retries=3, base_delay=1.0)
def fetch_single_page(url: str, headers: Dict, params: Dict) -> Dict:
    """
    Fetch single page with retry logic

    Args:
        url: API endpoint URL
        headers: Request headers including API key
        params: Query parameters

    Returns:
        JSON response as dictionary

    Raises:
        requests.exceptions.RequestException: On HTTP errors
    """
    response = requests.get(url, headers=headers, params=params, timeout=30)
    response.raise_for_status()
    return response.json()


def fetch_zillow_listings(
    status_type: str, config: Dict, api_key: str, max_pages: int = 20, page_delay: float = 0.5
) -> pd.DataFrame:
    """
    Generic Zillow listing fetcher for both for-sale and rental properties

    Args:
        status_type: 'ForSale' or 'ForRent'
        config: Dictionary with minPrice, maxPrice, beds, baths, sqft, buildYear
        api_key: RapidAPI key
        max_pages: Maximum pages to fetch
        page_delay: Delay between requests in seconds

    Returns:
        DataFrame with property listings
    """
    url = "https://zillow-com1.p.rapidapi.com/propertyByPolygon"
    polygon_coords = f"{NASHVILLE_POLYGON['west']} {NASHVILLE_POLYGON['north']}, {NASHVILLE_POLYGON['east']} {NASHVILLE_POLYGON['north']}, {NASHVILLE_POLYGON['east']} {NASHVILLE_POLYGON['south']}, {NASHVILLE_POLYGON['west']} {NASHVILLE_POLYGON['south']}, {NASHVILLE_POLYGON['west']} {NASHVILLE_POLYGON['north']}"

    headers = {"x-rapidapi-key": api_key, "x-rapidapi-host": "zillow-com1.p.rapidapi.com"}

    all_properties = []

    for page in range(1, max_pages + 1):
        querystring = {
            "polygon": polygon_coords,
            "status_type": status_type,
            "page": str(page),
            **{k: str(v) for k, v in config.items() if k not in ["max_pages", "page_delay"]},
        }

        try:
            logger.info(f"Fetching {status_type} page {page}/{max_pages}")
            data = fetch_single_page(url, headers, querystring)
            properties = data.get("props", [])

            if not properties:
                logger.info(f"No more properties found at page {page}, stopping pagination")
                break

            all_properties.extend(properties)
            logger.debug(f"Retrieved {len(properties)} properties from page {page}")

            time.sleep(page_delay)

        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed on page {page}: {e}")
            break
        except ValueError as e:
            logger.error(f"JSON decode error on page {page}: {e}")
            break
        except Exception as e:
            logger.error(f"Unexpected error on page {page}: {e}")
            break

    if all_properties:
        logger.info(f"Total {status_type} properties retrieved: {len(all_properties)}")
        df = pd.DataFrame(all_properties)
        df = validate_zillow_dataframe(df, status_type)
        return df
    else:
        logger.warning(f"No {status_type} properties retrieved")
        return pd.DataFrame()
