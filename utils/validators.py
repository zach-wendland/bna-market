"""
Data validation utilities for BNA Market application

Provides validation functions for API responses and data quality checks.
"""

import pandas as pd
from typing import Dict
from utils.logger import setup_logger
from utils.exceptions import DataValidationError

logger = setup_logger("validators")


def validate_zillow_property(prop: Dict) -> bool:
    """
    Validate single property has required fields

    Args:
        prop: Property dictionary from Zillow API

    Returns:
        True if valid, False otherwise
    """
    required_fields = ["zpid", "price", "address"]

    for field in required_fields:
        if field not in prop or prop[field] is None:
            logger.warning(
                f"Property missing required field '{field}': {prop.get('zpid', 'unknown')}"
            )
            return False

    # Validate data types
    if not isinstance(prop["zpid"], (int, str)):
        logger.warning(f"Invalid zpid type: {type(prop['zpid'])}")
        return False

    return True


def validate_zillow_dataframe(df: pd.DataFrame, status_type: str) -> pd.DataFrame:
    """
    Validate and clean Zillow property DataFrame

    Args:
        df: DataFrame with property listings
        status_type: 'forSale' or 'forRent'

    Returns:
        Cleaned and validated DataFrame

    Raises:
        DataValidationError: If DataFrame is missing required columns
    """
    if df.empty:
        logger.info(f"Empty DataFrame for {status_type}, nothing to validate")
        return df

    initial_count = len(df)

    # Check for required columns
    if "zpid" not in df.columns:
        raise DataValidationError(f"{status_type} DataFrame missing 'zpid' column")

    # Remove duplicates
    df = df.drop_duplicates(subset=["zpid"], keep="last")

    # Remove rows with null zpid
    df = df.dropna(subset=["zpid"])

    # Validate price ranges (basic sanity checks)
    if "price" in df.columns:
        df = df[df["price"] > 0]
        df = df[df["price"] < 100_000_000]  # $100M sanity check

    final_count = len(df)

    if final_count < initial_count:
        logger.info(
            f"Validation removed {initial_count - final_count} invalid {status_type} records"
        )

    logger.info(f"Validated {final_count} {status_type} properties")
    return df


def validate_fred_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Validate FRED metrics DataFrame

    Performs defensive validation on FRED data including:
    - Checking for required columns (date, metric_name, series_id, value)
    - Removing rows with null values
    - Ensuring date column is in string format for SQLite storage

    Note: Date conversion is defensive - the pipeline should convert dates to strings,
    but this validator handles cases where source data format varies.

    Args:
        df: DataFrame with FRED economic indicators

    Returns:
        Cleaned and validated DataFrame

    Raises:
        DataValidationError: If DataFrame is missing required columns
    """
    if df.empty:
        return df

    required_columns = ["date", "metric_name", "series_id", "value"]

    for col in required_columns:
        if col not in df.columns:
            raise DataValidationError(f"FRED DataFrame missing '{col}' column")

    # Remove rows with null values
    initial_count = len(df)
    df = df.dropna(subset=["date", "value"])

    # Convert date to string for SQLite storage (if not already string)
    if not pd.api.types.is_string_dtype(df["date"]):
        df["date"] = df["date"].dt.strftime("%Y-%m-%d")

    final_count = len(df)

    if final_count < initial_count:
        logger.info(f"Validation removed {initial_count - final_count} invalid FRED records")

    logger.info(f"Validated {final_count} FRED metric records")
    return df
