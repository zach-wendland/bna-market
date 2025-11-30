"""
Database index creation script for BNA Market

Adds indexes to improve query performance for common search patterns.
"""
import sqlite3
from utils.logger import setup_logger
from config.settings import DATABASE_CONFIG

logger = setup_logger('indexes')


def add_database_indexes():
    """Add indexes to improve query performance"""

    conn = sqlite3.connect(DATABASE_CONFIG['path'])
    cursor = conn.cursor()

    indexes = [
        # For-sale properties indexes
        "CREATE INDEX IF NOT EXISTS idx_forsale_zpid ON BNA_FORSALE(zpid)",
        "CREATE INDEX IF NOT EXISTS idx_forsale_price ON BNA_FORSALE(price)",
        "CREATE INDEX IF NOT EXISTS idx_forsale_city ON BNA_FORSALE(city)",
        "CREATE INDEX IF NOT EXISTS idx_forsale_bedrooms ON BNA_FORSALE(bedrooms)",
        "CREATE INDEX IF NOT EXISTS idx_forsale_bathrooms ON BNA_FORSALE(bathrooms)",

        # Rental properties indexes
        "CREATE INDEX IF NOT EXISTS idx_rentals_zpid ON BNA_RENTALS(zpid)",
        "CREATE INDEX IF NOT EXISTS idx_rentals_price ON BNA_RENTALS(price)",
        "CREATE INDEX IF NOT EXISTS idx_rentals_city ON BNA_RENTALS(city)",
        "CREATE INDEX IF NOT EXISTS idx_rentals_bedrooms ON BNA_RENTALS(bedrooms)",

        # FRED metrics indexes
        "CREATE INDEX IF NOT EXISTS idx_fred_date ON BNA_FRED_METRICS(date)",
        "CREATE INDEX IF NOT EXISTS idx_fred_series ON BNA_FRED_METRICS(series_id)",
        "CREATE INDEX IF NOT EXISTS idx_fred_metric ON BNA_FRED_METRICS(metric_name)",
        "CREATE INDEX IF NOT EXISTS idx_fred_composite ON BNA_FRED_METRICS(date, series_id)"
    ]

    for idx_sql in indexes:
        try:
            cursor.execute(idx_sql)
            index_name = idx_sql.split('idx_')[1].split(' ON')[0]
            logger.info(f"Created index: idx_{index_name}")
        except sqlite3.Error as e:
            logger.error(f"Index creation failed: {e}")

    conn.commit()
    conn.close()
    logger.info("All indexes created successfully")


if __name__ == '__main__':
    logger.info("Starting database index creation")
    add_database_indexes()
    logger.info("Database index creation complete")
