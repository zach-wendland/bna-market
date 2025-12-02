"""Integration tests for ETL workflows"""

import pytest
import pandas as pd
from unittest.mock import patch
from app import updateSalesTable, updateRentalsTable, updateFredMetricsTable


class TestETLWorkflows:
    """Integration tests for ETL update functions"""

    @patch("app.forSalePipe01")
    @patch("app.get_db_connection")
    def test_update_sales_table_with_new_data(
        self, mock_db_conn, mock_pipeline, sample_forsale_df, temp_db
    ):
        """Should successfully update sales table with new data"""
        import sqlite3

        mock_pipeline.return_value = sample_forsale_df

        # Mock database connection to use temp_db
        class MockContextManager:
            def __enter__(self):
                return sqlite3.connect(temp_db)

            def __exit__(self, *args):
                pass

        mock_db_conn.return_value = MockContextManager()

        # Should not raise exception
        updateSalesTable()

        # Verify data was written
        conn = sqlite3.connect(temp_db)
        result = pd.read_sql_query("SELECT * FROM BNA_FORSALE", conn)
        conn.close()

        assert len(result) == 2
        assert result["zpid"].tolist() == [12345, 67890]

    @patch("app.rentalPipe01")
    @patch("app.get_db_connection")
    def test_update_rentals_table_with_new_data(
        self, mock_db_conn, mock_pipeline, sample_rental_df, temp_db
    ):
        """Should successfully update rentals table with new data"""
        import sqlite3

        mock_pipeline.return_value = sample_rental_df

        class MockContextManager:
            def __enter__(self):
                return sqlite3.connect(temp_db)

            def __exit__(self, *args):
                pass

        mock_db_conn.return_value = MockContextManager()

        updateRentalsTable()

        conn = sqlite3.connect(temp_db)
        result = pd.read_sql_query("SELECT * FROM BNA_RENTALS", conn)
        conn.close()

        assert len(result) == 2

    @patch("app.fredMetricsPipe01")
    @patch("app.get_db_connection")
    def test_update_fred_table_with_new_data(
        self, mock_db_conn, mock_pipeline, sample_fred_df, temp_db
    ):
        """Should successfully update FRED metrics table"""
        import sqlite3

        mock_pipeline.return_value = sample_fred_df

        class MockContextManager:
            def __enter__(self):
                return sqlite3.connect(temp_db)

            def __exit__(self, *args):
                pass

        mock_db_conn.return_value = MockContextManager()

        updateFredMetricsTable()

        conn = sqlite3.connect(temp_db)
        result = pd.read_sql_query("SELECT * FROM BNA_FRED_METRICS", conn)
        conn.close()

        assert len(result) == 3

    @patch("app.forSalePipe01")
    def test_update_sales_skips_empty_dataframe(self, mock_pipeline):
        """Should skip update when pipeline returns empty DataFrame"""
        mock_pipeline.return_value = pd.DataFrame()

        # Should not raise exception
        updateSalesTable()

    @patch("app.forSalePipe01")
    @patch("app.get_db_connection")
    def test_update_sales_deduplicates_on_zpid(
        self, mock_db_conn, mock_pipeline, temp_db
    ):
        """Should deduplicate records based on zpid"""
        import sqlite3

        # Insert initial data
        conn = sqlite3.connect(temp_db)
        conn.execute(
            "INSERT INTO BNA_FORSALE VALUES (12345, 350000, '123 Main', 3, 2.0, 1800)"
        )
        conn.commit()
        conn.close()

        # New data with same zpid but updated price
        new_data = pd.DataFrame(
            {
                "zpid": [12345],
                "price": [360000],  # Updated price
                "address": ["123 Main"],
                "bedrooms": [3],
                "bathrooms": [2.0],
                "livingArea": [1800],
            }
        )
        mock_pipeline.return_value = new_data

        class MockContextManager:
            def __enter__(self):
                return sqlite3.connect(temp_db)

            def __exit__(self, *args):
                pass

        mock_db_conn.return_value = MockContextManager()

        updateSalesTable()

        conn = sqlite3.connect(temp_db)
        result = pd.read_sql_query("SELECT * FROM BNA_FORSALE WHERE zpid = 12345", conn)
        conn.close()

        assert len(result) == 1
        assert result.iloc[0]["price"] == 360000  # Should have updated price
