"""
ETL orchestration service for BNA Market

Coordinates data pipeline execution and database updates with deduplication logic.
"""

import json

import pandas as pd

from bna_market.pipelines.for_sale import fetch_for_sale_properties
from bna_market.pipelines.rental import fetch_rental_properties
from bna_market.pipelines.fred_metrics import fetch_fred_metrics
from bna_market.utils.logger import setup_logger
from bna_market.utils.database import get_db_connection, read_table_safely
from bna_market.utils.env_validator import validate_environment
from bna_market.core.config import settings, DATABASE_CONFIG

logger = setup_logger("etl_service")


class ETLService:
    """
    Orchestrates ETL pipeline execution and database updates

    Handles fetching data from external APIs, merging with existing database records,
    deduplication, and table updates.

    Attributes:
        db_path: Path to SQLite database file

    Example:
        >>> service = ETLService()
        >>> results = service.run_full_refresh()
        >>> print(f"Updated {results['for_sale']} for-sale properties")
    """

    def __init__(self, db_path: str | None = None):
        """
        Initialize ETL service

        Args:
            db_path: Optional custom database path (defaults to settings database_path)
        """
        self.db_path = db_path or DATABASE_CONFIG["path"]
        self.logger = setup_logger("etl_service")

    def update_sales_table(self) -> int:
        """
        Update BNA_FORSALE table with latest Zillow for-sale properties

        Fetches new data from Zillow API, merges with existing database records,
        deduplicates on zpid, and replaces table contents.

        Returns:
            Number of records in updated table (0 if update skipped)

        Example:
            >>> service = ETLService()
            >>> count = service.update_sales_table()
            >>> print(f"Updated {count} for-sale records")
        """
        self.logger.info("Starting for-sale properties update")

        df = fetch_for_sale_properties()

        # Skip if no data was fetched
        if df.empty:
            self.logger.warning("Skipping BNA_FORSALE table update - no data available")
            return 0

        with get_db_connection(self.db_path) as conn:
            # Read existing data
            existing_df = read_table_safely("BNA_FORSALE", conn)

            # Merge new data with existing, keeping only new rows based on zpid
            if not existing_df.empty and "zpid" in df.columns and "zpid" in existing_df.columns:
                df = pd.concat([existing_df, df]).drop_duplicates(subset=["zpid"], keep="last")
                self.logger.info(f"Merged with {len(existing_df)} existing records")

            # Convert dict/list to JSON strings for SQLite
            df = df.map(lambda x: json.dumps(x) if isinstance(x, (dict, list)) else x)

            df.to_sql(name="BNA_FORSALE", con=conn, if_exists="replace", index=False)
            self.logger.info(f"Updated BNA_FORSALE: {len(df)} total records")

            return len(df)

    def update_rentals_table(self) -> int:
        """
        Update BNA_RENTALS table with latest Zillow rental properties

        Fetches new data from Zillow API, merges with existing database records,
        deduplicates on zpid, and replaces table contents.

        Returns:
            Number of records in updated table (0 if update skipped)

        Example:
            >>> service = ETLService()
            >>> count = service.update_rentals_table()
            >>> print(f"Updated {count} rental records")
        """
        self.logger.info("Starting rental properties update")

        df = fetch_rental_properties()

        # Skip if no data was fetched
        if df.empty:
            self.logger.warning("Skipping BNA_RENTALS table update - no data available")
            return 0

        with get_db_connection(self.db_path) as conn:
            # Read existing data
            existing_df = read_table_safely("BNA_RENTALS", conn)

            # Merge new data with existing, keeping only new rows based on zpid
            if not existing_df.empty and "zpid" in df.columns and "zpid" in existing_df.columns:
                df = pd.concat([existing_df, df]).drop_duplicates(subset=["zpid"], keep="last")
                self.logger.info(f"Merged with {len(existing_df)} existing records")

            # Convert dict/list to JSON strings for SQLite
            df = df.map(lambda x: json.dumps(x) if isinstance(x, (dict, list)) else x)

            df.to_sql(name="BNA_RENTALS", con=conn, if_exists="replace", index=False)
            self.logger.info(f"Updated BNA_RENTALS: {len(df)} total records")

            return len(df)

    def update_fred_metrics_table(self) -> int:
        """
        Update BNA_FRED_METRICS table with latest FRED economic indicators

        Fetches new data from FRED API, merges with existing database records,
        deduplicates on date + series_id, and replaces table contents.

        Returns:
            Number of records in updated table (0 if update skipped)

        Example:
            >>> service = ETLService()
            >>> count = service.update_fred_metrics_table()
            >>> print(f"Updated {count} FRED metric observations")
        """
        self.logger.info("Starting FRED metrics update")

        df = fetch_fred_metrics()

        # Skip if no data was fetched
        if df.empty:
            self.logger.warning("Skipping BNA_FRED_METRICS table update - no data available")
            return 0

        with get_db_connection(self.db_path) as conn:
            # Read existing data
            existing_df = read_table_safely("BNA_FRED_METRICS", conn)

            # Merge and deduplicate based on date + series_id
            if not existing_df.empty:
                df = pd.concat([existing_df, df]).drop_duplicates(
                    subset=["date", "series_id"], keep="last"
                )
                self.logger.info(f"Merged with {len(existing_df)} existing records")

            df.to_sql(name="BNA_FRED_METRICS", con=conn, if_exists="replace", index=False)
            self.logger.info(f"Updated BNA_FRED_METRICS: {len(df)} total records")

            return len(df)

    def run_full_refresh(self) -> dict[str, int]:
        """
        Run all ETL pipelines and update all tables

        Validates environment before execution, then runs all three pipelines
        sequentially (for-sale, rentals, FRED metrics).

        Returns:
            Dictionary with row counts for each table

        Raises:
            SystemExit: If environment validation fails

        Example:
            >>> service = ETLService()
            >>> results = service.run_full_refresh()
            >>> print(f"Results: {results}")
            {'for_sale': 1234, 'rentals': 567, 'fred_metrics': 8900}
        """
        self.logger.info("=" * 60)
        self.logger.info("BNA Market ETL Pipeline Started")
        self.logger.info("=" * 60)

        # Validate environment before running pipelines
        if not validate_environment():
            self.logger.error("Environment validation failed, exiting")
            raise SystemExit(1)

        results = {}

        try:
            # Execute all update functions
            results["for_sale"] = self.update_sales_table()
            results["rentals"] = self.update_rentals_table()
            results["fred_metrics"] = self.update_fred_metrics_table()

            self.logger.info("=" * 60)
            self.logger.info("BNA Market ETL Pipeline Completed Successfully")
            self.logger.info(f"Results: {results}")
            self.logger.info("=" * 60)

            return results

        except Exception as e:
            self.logger.error(f"Pipeline failed with error: {e}", exc_info=True)
            raise


# Backwards compatibility function for legacy code
def run_etl() -> dict[str, int]:
    """
    Legacy function for backwards compatibility

    Use ETLService().run_full_refresh() instead.

    Returns:
        Dictionary with row counts for each table
    """
    service = ETLService()
    return service.run_full_refresh()
