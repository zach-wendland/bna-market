"""
ETL orchestration service for BNA Market

Coordinates data pipeline execution and database updates with Supabase upserts.
"""

import json
from datetime import datetime

import pandas as pd

from bna_market.pipelines.for_sale import fetch_for_sale_properties
from bna_market.pipelines.rental import fetch_rental_properties
from bna_market.pipelines.fred_metrics import fetch_fred_metrics
from bna_market.utils.logger import setup_logger
from bna_market.utils.database import upsert_dataframe, read_table_safely
from bna_market.utils.env_validator import validate_environment
from bna_market.core.config import DATABASE_CONFIG

logger = setup_logger("etl_service")


class ETLService:
    """
    Orchestrates ETL pipeline execution and database updates

    Handles fetching data from external APIs, deduplication, and Supabase upserts.

    Example:
        >>> service = ETLService()
        >>> results = service.run_full_refresh()
        >>> print(f"Updated {results['for_sale']} for-sale properties")
    """

    def __init__(self):
        """Initialize ETL service"""
        self.logger = setup_logger("etl_service")

    def _prepare_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Prepare DataFrame for Supabase insertion

        Converts complex types to JSON strings and handles NaN values.

        Args:
            df: Input DataFrame

        Returns:
            Cleaned DataFrame ready for insertion
        """
        if df.empty:
            return df

        # Make a copy to avoid modifying original
        df = df.copy()

        # Convert dict/list columns to JSON strings
        for col in df.columns:
            df[col] = df[col].apply(
                lambda x: json.dumps(x) if isinstance(x, (dict, list)) else x
            )

        # Replace NaN with None for PostgreSQL compatibility
        df = df.where(pd.notnull(df), None)

        return df

    def update_sales_table(self) -> int:
        """
        Update bna_forsale table with latest Zillow for-sale properties

        Fetches new data from Zillow API and upserts to Supabase.

        Returns:
            Number of records upserted (0 if update skipped)

        Example:
            >>> service = ETLService()
            >>> count = service.update_sales_table()
            >>> print(f"Updated {count} for-sale records")
        """
        self.logger.info("Starting for-sale properties update")

        df = fetch_for_sale_properties()

        # Skip if no data was fetched
        if df.empty:
            self.logger.warning("Skipping bna_forsale table update - no data available")
            return 0

        # Prepare data for insertion
        df = self._prepare_dataframe(df)

        # Upsert to Supabase
        count = upsert_dataframe(
            df,
            table_name="bna_forsale",
            unique_columns=DATABASE_CONFIG["unique_keys"]["for_sale"]
        )

        self.logger.info(f"Updated bna_forsale: {count} records upserted")
        return count

    def update_rentals_table(self) -> int:
        """
        Update bna_rentals table with latest Zillow rental properties

        Fetches new data from Zillow API and upserts to Supabase.

        Returns:
            Number of records upserted (0 if update skipped)

        Example:
            >>> service = ETLService()
            >>> count = service.update_rentals_table()
            >>> print(f"Updated {count} rental records")
        """
        self.logger.info("Starting rental properties update")

        df = fetch_rental_properties()

        # Skip if no data was fetched
        if df.empty:
            self.logger.warning("Skipping bna_rentals table update - no data available")
            return 0

        # Prepare data for insertion
        df = self._prepare_dataframe(df)

        # Upsert to Supabase
        count = upsert_dataframe(
            df,
            table_name="bna_rentals",
            unique_columns=DATABASE_CONFIG["unique_keys"]["rentals"]
        )

        self.logger.info(f"Updated bna_rentals: {count} records upserted")
        return count

    def update_fred_metrics_table(self) -> int:
        """
        Update bna_fred_metrics table with latest FRED economic indicators

        Fetches new data from FRED API and upserts to Supabase.

        Returns:
            Number of records upserted (0 if update skipped)

        Example:
            >>> service = ETLService()
            >>> count = service.update_fred_metrics_table()
            >>> print(f"Updated {count} FRED metric observations")
        """
        self.logger.info("Starting FRED metrics update")

        df = fetch_fred_metrics()

        # Skip if no data was fetched
        if df.empty:
            self.logger.warning("Skipping bna_fred_metrics table update - no data available")
            return 0

        # Convert date column to string format for PostgreSQL DATE type
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")

        # Prepare data for insertion
        df = self._prepare_dataframe(df)

        # Upsert to Supabase
        count = upsert_dataframe(
            df,
            table_name="bna_fred_metrics",
            unique_columns=DATABASE_CONFIG["unique_keys"]["fred_metrics"]
        )

        self.logger.info(f"Updated bna_fred_metrics: {count} records upserted")
        return count

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
