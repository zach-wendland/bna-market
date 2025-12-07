"""
Database utilities for BNA Market application

Provides context managers and helper functions for safe database operations.
"""

import sqlite3
import pandas as pd
from contextlib import contextmanager
from typing import Optional
from bna_market.utils.logger import setup_logger
from bna_market.core.config import DATABASE_CONFIG

logger = setup_logger("database")


@contextmanager
def get_db_connection(db_path: Optional[str] = None):
    """
    Context manager for database connections with automatic commit/rollback

    Args:
        db_path: Path to SQLite database file (default: from config)

    Yields:
        sqlite3.Connection: Database connection

    Example:
        with get_db_connection() as conn:
            df.to_sql('table_name', conn, if_exists='replace')
    """
    path = db_path or DATABASE_CONFIG["path"]
    conn = sqlite3.connect(path)
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Database transaction failed: {e}")
        raise
    finally:
        conn.close()


# Valid table names whitelist to prevent SQL injection
VALID_TABLE_NAMES = frozenset([
    "BNA_FORSALE",
    "BNA_RENTALS",
    "BNA_FRED_METRICS",
])


def read_table_safely(table_name: str, conn: sqlite3.Connection) -> pd.DataFrame:
    """
    Read table with proper error handling and SQL injection protection

    Args:
        table_name: Name of the table to read (must be in VALID_TABLE_NAMES)
        conn: Database connection

    Returns:
        DataFrame with table contents, or empty DataFrame if table doesn't exist

    Raises:
        ValueError: If table_name is not in the allowed whitelist
        sqlite3.DatabaseError: For database errors other than missing table
    """
    # Validate table name against whitelist to prevent SQL injection
    if table_name not in VALID_TABLE_NAMES:
        raise ValueError(
            f"Invalid table name '{table_name}'. "
            f"Must be one of: {', '.join(sorted(VALID_TABLE_NAMES))}"
        )

    try:
        df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
        logger.debug(f"Read {len(df)} rows from {table_name}")
        return df
    except (sqlite3.OperationalError, pd.errors.DatabaseError) as e:
        # Handle both missing tables and pandas-wrapped database errors
        error_msg = str(e).lower()
        if "no such table" in error_msg or "doesn't exist" in error_msg:
            logger.info(f"Table {table_name} doesn't exist yet")
            return pd.DataFrame()
        else:
            logger.error(f"Database error reading {table_name}: {e}")
            raise
