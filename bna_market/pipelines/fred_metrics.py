"""
FRED economic indicators pipeline for BNA Market

Fetches Nashville MSA economic indicators from FRED API with retry logic and validation.
"""

import requests
from datetime import datetime, timedelta

import pandas as pd
from fredapi import Fred

from bna_market.core.config import FRED_CONFIG, settings
from bna_market.utils.logger import setup_logger
from bna_market.utils.retry import retry_with_backoff
from bna_market.utils.validators import validate_fred_dataframe

logger = setup_logger("fred_pipeline")


@retry_with_backoff(
    max_retries=3,
    base_delay=1.0,
    retry_on=(requests.exceptions.RequestException,)
)
def fetch_fred_series(
    fred: Fred,
    series_id: str,
    start_date: str,
    end_date: str
) -> pd.Series:
    """
    Fetch single FRED series with retry logic

    Args:
        fred: FRED API client instance
        series_id: FRED series identifier (e.g., "MEDLISPRI34980")
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format

    Returns:
        Time series data with dates as index

    Raises:
        Exception: On API errors after retry exhaustion

    Example:
        >>> fred = Fred(api_key="...")
        >>> series = fetch_fred_series(fred, "MEDLISPRI34980", "2020-01-01", "2024-01-01")
    """
    return fred.get_series(
        series_id,
        observation_start=start_date,
        observation_end=end_date
    )


def fetch_fred_metrics() -> pd.DataFrame:
    """
    Fetch FRED economic indicators for Nashville MSA

    Fetches 8 economic indicator series for the Nashville MSA:
    - Active listings count
    - Median listing price
    - Median days on market
    - Non-farm employment
    - MSA population
    - Median price per square foot
    - Median listing price change
    - MSA per capita income

    Returns:
        Long-format DataFrame with economic indicator time series data
        Columns: date (YYYY-MM-DD string), metric_name, series_id, value

    Raises:
        ValueError: If FRED_API_KEY is not found in environment

    Example:
        >>> df = fetch_fred_metrics()
        >>> print(df.groupby('metric_name').size())
    """
    # Import os here to check environment directly (for test compatibility)
    import os
    api_key = os.getenv("FRED_API_KEY", "")
    if not api_key:
        raise ValueError("FRED_API_KEY not found in environment")

    fred = Fred(api_key=api_key)

    # Calculate date range: configurable years back from today
    end_date = datetime.now()
    start_date = end_date - timedelta(days=FRED_CONFIG["years_historical"] * 365)

    logger.info(
        f"Fetching FRED data from {start_date.date()} to {end_date.date()} "
        f"({FRED_CONFIG['years_historical']} years)"
    )

    # Fetch all series and combine into single DataFrame
    all_data: list[pd.DataFrame] = []
    series_list = list(FRED_CONFIG["series_ids"].items())
    failed_series: list[str] = []

    for metric_name, series_id in series_list:
        try:
            logger.info(f"Fetching {metric_name} ({series_id})")

            # Fetch series data with observation start/end dates
            series = fetch_fred_series(
                fred,
                series_id,
                start_date.strftime("%Y-%m-%d"),
                end_date.strftime("%Y-%m-%d")
            )

            # Convert to DataFrame with date formatting
            # Date is converted to string format for SQLite compatibility
            df = series.to_frame(name="value")
            df["metric_name"] = metric_name
            df["series_id"] = series_id
            df.reset_index(inplace=True)
            df.rename(columns={"index": "date"}, inplace=True)
            df["date"] = df["date"].dt.strftime("%Y-%m-%d")

            all_data.append(df)
            logger.debug(f"Fetched {len(df)} observations for {metric_name}")

        except Exception as e:
            logger.warning(f"Error fetching {metric_name} ({series_id}): {e}")
            failed_series.append(metric_name)
            continue

    # Alert if too many series failed (more than 50%)
    success_count = len(all_data)
    total_count = len(series_list)
    failure_count = total_count - success_count

    if failure_count > total_count * 0.5:
        logger.error(
            f"CRITICAL: {failure_count}/{total_count} FRED series failed to fetch. "
            f"Failed series: {', '.join(failed_series)}"
        )
    elif failure_count > 0:
        logger.warning(
            f"WARNING: {failure_count}/{total_count} FRED series failed to fetch. "
            f"Failed series: {', '.join(failed_series)}"
        )

    if all_data:
        result_df = pd.concat(all_data, ignore_index=True)
        logger.info(f"Total observations collected: {len(result_df)}")

        # Validate the DataFrame
        result_df = validate_fred_dataframe(result_df)

        return result_df
    else:
        logger.warning("No FRED data was collected")
        return pd.DataFrame(columns=["date", "metric_name", "series_id", "value"])
