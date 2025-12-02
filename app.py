"""
ETL orchestration for BNA Market

Coordinates data pipeline execution and database updates.
"""

import pandas as pd
import json
from pipelines.forSale import forSalePipe01
from pipelines.rentalPipe import rentalPipe01
from pipelines.otherMetricsPipe import fredMetricsPipe01
from utils.logger import setup_logger
from utils.database import get_db_connection, read_table_safely
from utils.env_validator import validate_environment
from config.settings import DATABASE_CONFIG

logger = setup_logger("app")


def updateSalesTable() -> None:
    """
    Update BNA_FORSALE table with latest Zillow for-sale properties

    Fetches new data from Zillow API, merges with existing database records,
    deduplicates on zpid, and replaces table contents.
    """
    logger.info("Starting for-sale properties update")

    df = forSalePipe01()

    # Skip if no data was fetched
    if df.empty:
        logger.warning("Skipping BNA_FORSALE table update - no data available")
        return

    with get_db_connection() as conn:
        # Read existing data
        existing_df = read_table_safely("BNA_FORSALE", conn)

        # Merge new data with existing, keeping only new rows based on zpid
        if not existing_df.empty and "zpid" in df.columns and "zpid" in existing_df.columns:
            df = pd.concat([existing_df, df]).drop_duplicates(subset=["zpid"], keep="last")
            logger.info(f"Merged with {len(existing_df)} existing records")

        # Convert dict/list to JSON strings for SQLite
        df = df.map(lambda x: json.dumps(x) if isinstance(x, (dict, list)) else x)

        df.to_sql(name="BNA_FORSALE", con=conn, if_exists="replace", index=False)
        logger.info(f"Updated BNA_FORSALE: {len(df)} total records")


def updateRentalsTable() -> None:
    """
    Update BNA_RENTALS table with latest Zillow rental properties

    Fetches new data from Zillow API, merges with existing database records,
    deduplicates on zpid, and replaces table contents.
    """
    logger.info("Starting rental properties update")

    df = rentalPipe01()

    # Skip if no data was fetched
    if df.empty:
        logger.warning("Skipping BNA_RENTALS table update - no data available")
        return

    with get_db_connection() as conn:
        # Read existing data
        existing_df = read_table_safely("BNA_RENTALS", conn)

        # Merge new data with existing, keeping only new rows based on zpid
        if not existing_df.empty and "zpid" in df.columns and "zpid" in existing_df.columns:
            df = pd.concat([existing_df, df]).drop_duplicates(subset=["zpid"], keep="last")
            logger.info(f"Merged with {len(existing_df)} existing records")

        # Convert dict/list to JSON strings for SQLite
        df = df.map(lambda x: json.dumps(x) if isinstance(x, (dict, list)) else x)

        df.to_sql(name="BNA_RENTALS", con=conn, if_exists="replace", index=False)
        logger.info(f"Updated BNA_RENTALS: {len(df)} total records")


def updateFredMetricsTable() -> None:
    """
    Update BNA_FRED_METRICS table with latest FRED economic indicators

    Fetches new data from FRED API, merges with existing database records,
    deduplicates on date + series_id, and replaces table contents.
    """
    logger.info("Starting FRED metrics update")

    df = fredMetricsPipe01()

    # Skip if no data was fetched
    if df.empty:
        logger.warning("Skipping BNA_FRED_METRICS table update - no data available")
        return

    with get_db_connection() as conn:
        # Read existing data
        existing_df = read_table_safely("BNA_FRED_METRICS", conn)

        # Merge and deduplicate based on date + series_id
        if not existing_df.empty:
            df = pd.concat([existing_df, df]).drop_duplicates(
                subset=["date", "series_id"], keep="last"
            )
            logger.info(f"Merged with {len(existing_df)} existing records")

        df.to_sql(name="BNA_FRED_METRICS", con=conn, if_exists="replace", index=False)
        logger.info(f"Updated BNA_FRED_METRICS: {len(df)} total records")


if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("BNA Market ETL Pipeline Started")
    logger.info("=" * 60)

    # Validate environment before running pipelines
    if not validate_environment():
        logger.error("Environment validation failed, exiting")
        exit(1)

    try:
        # Execute all update functions
        updateSalesTable()
        updateRentalsTable()
        updateFredMetricsTable()

        logger.info("=" * 60)
        logger.info("BNA Market ETL Pipeline Completed Successfully")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"Pipeline failed with error: {e}", exc_info=True)
        exit(1)
