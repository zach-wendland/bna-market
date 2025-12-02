"""
Database utilities for BNA Market application

Provides context managers and helper functions for safe database operations.
"""

import sqlite3
import pandas as pd
from contextlib import contextmanager
from typing import Optional
from utils.logger import setup_logger
from config.settings import DATABASE_CONFIG

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


def read_table_safely(table_name: str, conn: sqlite3.Connection) -> pd.DataFrame:
    """
    Read table with proper error handling

    Args:
        table_name: Name of the table to read
        conn: Database connection

    Returns:
        DataFrame with table contents, or empty DataFrame if table doesn't exist

    Raises:
        sqlite3.DatabaseError: For database errors other than missing table
    """
    try:
        df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
        logger.debug(f"Read {len(df)} rows from {table_name}")
        return df
    except sqlite3.OperationalError:
        logger.info(f"Table {table_name} doesn't exist yet")
        return pd.DataFrame()
    except sqlite3.DatabaseError as e:
        logger.error(f"Database error reading {table_name}: {e}")
        raise
