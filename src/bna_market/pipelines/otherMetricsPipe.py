"""
FRED economic indicators pipeline for BNA Market

Fetches Nashville MSA economic indicators from FRED API.
"""

from fredapi import Fred
import pandas as pd
import os
import requests
from dotenv import load_dotenv
from datetime import datetime, timedelta
from bna_market.utils.logger import setup_logger
from bna_market.utils.retry import retry_with_backoff
from bna_market.utils.validators import validate_fred_dataframe
from bna_market.core.settings import FRED_CONFIG

load_dotenv()
logger = setup_logger("fred_pipeline")


@retry_with_backoff(max_retries=3, base_delay=1.0, retry_on=(requests.exceptions.RequestException,))
def fetch_fred_series(fred: Fred, series_id: str, start_date: str, end_date: str) -> pd.Series:
    """
    Fetch single FRED series with retry logic

    Args:
        fred: FRED API client instance
        series_id: FRED series identifier
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format

    Returns:
        Time series data

    Raises:
        Exception: On API errors
    """
    return fred.get_series(series_id, observation_start=start_date, observation_end=end_date)


def fredMetricsPipe01() -> pd.DataFrame:
    """
    Fetch FRED economic indicators for Nashville MSA

    Returns:
        Long-format DataFrame with economic indicator time series data
        Columns: date, metric_name, series_id, value

    Raises:
        ValueError: If FRED_API_KEY is not found in environment
    """
    api_key = os.getenv("FRED_API_KEY")
    if not api_key:
        raise ValueError("FRED_API_KEY not found in environment")

    fred = Fred(api_key=api_key)

    # Calculate date range: configurable years back from today
    end_date = datetime.now()
    start_date = end_date - timedelta(days=FRED_CONFIG["years_historical"] * 365)

    logger.info(f"Fetching FRED data from {start_date.date()} to {end_date.date()}")

    # Fetch all series and combine into single DataFrame
    all_data = []
    series_list = list(FRED_CONFIG["series_ids"].items())
    failed_series = []

    for metric_name, series_id in series_list:
        try:
            logger.info(f"Fetching {metric_name} ({series_id})")

            # Fetch series data with observation start/end dates
            series = fetch_fred_series(
                fred, series_id, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")
            )

            # Convert to DataFrame with date formatting
            # Note: Date is converted to string format here for SQLite compatibility.
            # The validate_fred_dataframe() function also handles date conversion defensively
            # in case data format varies from different sources.
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


if __name__ == "__main__":
    # Test the pipeline
    df = fredMetricsPipe01()
    print(f"\nCollected {len(df)} FRED metric observations")
    if not df.empty:
        print(f"Metrics: {df['metric_name'].unique().tolist()}")
        print(f"Date range: {df['date'].min()} to {df['date'].max()}")
