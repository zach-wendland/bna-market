"""
Database utilities for BNA Market application

Provides Supabase client and PostgreSQL connection management for database operations.
"""

import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from typing import Optional, Any
from urllib.parse import urlparse

from supabase import create_client, Client

from bna_market.utils.logger import setup_logger
from bna_market.core.config import SUPABASE_CONFIG, DATABASE_CONFIG

logger = setup_logger("database")

# Supabase client singleton
_supabase_client: Optional[Client] = None


def get_supabase_client(use_service_key: bool = False) -> Client:
    """
    Get Supabase client (singleton pattern)

    Args:
        use_service_key: If True, use service key for write operations (ETL).
                        If False, use anon key for read-only operations (API).

    Returns:
        Supabase client instance

    Raises:
        ValueError: If Supabase URL or key is not configured
    """
    global _supabase_client

    url = SUPABASE_CONFIG["url"]
    key = SUPABASE_CONFIG["service_key"] if use_service_key else SUPABASE_CONFIG["anon_key"]

    if not url:
        raise ValueError("SUPABASE_URL environment variable is not set")
    if not key:
        key_type = "SUPABASE_SERVICE_KEY" if use_service_key else "SUPABASE_ANON_KEY"
        raise ValueError(f"{key_type} environment variable is not set")

    # For service key operations, always create a new client
    if use_service_key:
        return create_client(url, key)

    # For anon key operations, use singleton
    if _supabase_client is None:
        _supabase_client = create_client(url, key)

    return _supabase_client


def get_postgres_connection_string() -> str:
    """
    Build PostgreSQL connection string from Supabase URL

    Supabase provides a connection string format for direct PostgreSQL access.
    We derive it from the project URL.

    Returns:
        PostgreSQL connection string
    """
    url = SUPABASE_CONFIG["url"]
    service_key = SUPABASE_CONFIG["service_key"]

    if not url:
        raise ValueError("SUPABASE_URL environment variable is not set")

    # Parse the Supabase URL to extract project reference
    # Format: https://<project-ref>.supabase.co
    parsed = urlparse(url)
    host = parsed.netloc  # e.g., "abcdefgh.supabase.co"

    # Supabase PostgreSQL connection format
    # Host: db.<project-ref>.supabase.co
    # Port: 5432 (default) or 6543 (pooler)
    project_ref = host.split(".")[0]
    pg_host = f"db.{project_ref}.supabase.co"

    # Use service key password for connection
    # In Supabase, you can use the database password from dashboard
    # or use the service_role key for programmatic access
    return f"postgresql://postgres.{project_ref}:{service_key}@{pg_host}:5432/postgres"


@contextmanager
def get_db_connection():
    """
    Context manager for PostgreSQL database connections with automatic commit/rollback

    Uses Supabase's PostgreSQL database directly for SQL queries.
    This maintains compatibility with the existing cursor-based query pattern.

    Yields:
        psycopg2 connection object

    Example:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM bna_forsale")
    """
    conn = None
    try:
        # Get connection parameters from Supabase config
        url = SUPABASE_CONFIG["url"]
        service_key = SUPABASE_CONFIG["service_key"]

        if not url or not service_key:
            raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set")

        # Parse project reference from URL
        parsed = urlparse(url)
        project_ref = parsed.netloc.split(".")[0]

        # Connect to Supabase PostgreSQL
        # Use the pooler for better serverless performance
        conn = psycopg2.connect(
            host=f"aws-0-us-east-1.pooler.supabase.com",
            port=6543,
            database="postgres",
            user=f"postgres.{project_ref}",
            password=service_key,
            sslmode="require",
        )

        yield conn
        conn.commit()

    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Database transaction failed: {e}")
        raise

    finally:
        if conn:
            conn.close()


# Valid table names whitelist to prevent SQL injection
VALID_TABLE_NAMES = frozenset([
    "bna_forsale",
    "bna_rentals",
    "bna_fred_metrics",
])


def read_table_safely(table_name: str, conn: Any = None) -> pd.DataFrame:
    """
    Read table with proper error handling and SQL injection protection

    Args:
        table_name: Name of the table to read (must be in VALID_TABLE_NAMES)
        conn: Optional database connection (if None, creates a new one)

    Returns:
        DataFrame with table contents, or empty DataFrame if table doesn't exist

    Raises:
        ValueError: If table_name is not in the allowed whitelist
    """
    # Normalize table name to lowercase for PostgreSQL
    table_name_lower = table_name.lower()

    # Validate table name against whitelist to prevent SQL injection
    if table_name_lower not in VALID_TABLE_NAMES:
        raise ValueError(
            f"Invalid table name '{table_name}'. "
            f"Must be one of: {', '.join(sorted(VALID_TABLE_NAMES))}"
        )

    try:
        if conn is not None:
            # Use provided connection
            df = pd.read_sql(f"SELECT * FROM {table_name_lower}", conn)
        else:
            # Create new connection
            with get_db_connection() as new_conn:
                df = pd.read_sql(f"SELECT * FROM {table_name_lower}", new_conn)

        logger.debug(f"Read {len(df)} rows from {table_name_lower}")
        return df

    except (psycopg2.Error, pd.errors.DatabaseError) as e:
        error_msg = str(e).lower()
        if "does not exist" in error_msg or "relation" in error_msg:
            logger.info(f"Table {table_name_lower} doesn't exist yet")
            return pd.DataFrame()
        else:
            logger.error(f"Database error reading {table_name_lower}: {e}")
            raise


def upsert_dataframe(
    df: pd.DataFrame,
    table_name: str,
    unique_columns: list[str],
    use_service_key: bool = True
) -> int:
    """
    Upsert DataFrame to Supabase table using ON CONFLICT

    Args:
        df: DataFrame to upsert
        table_name: Target table name
        unique_columns: Columns that form the unique constraint
        use_service_key: Use service key for write access

    Returns:
        Number of rows upserted
    """
    if df.empty:
        logger.warning(f"Empty DataFrame, skipping upsert to {table_name}")
        return 0

    # Normalize table name
    table_name_lower = table_name.lower()

    if table_name_lower not in VALID_TABLE_NAMES:
        raise ValueError(f"Invalid table name '{table_name}'")

    try:
        client = get_supabase_client(use_service_key=use_service_key)

        # Convert DataFrame to list of dicts
        records = df.to_dict(orient="records")

        # Supabase upsert
        result = client.table(table_name_lower).upsert(
            records,
            on_conflict=",".join(unique_columns)
        ).execute()

        count = len(result.data) if result.data else len(records)
        logger.info(f"Upserted {count} rows to {table_name_lower}")
        return count

    except Exception as e:
        logger.error(f"Upsert failed for {table_name_lower}: {e}")
        raise
