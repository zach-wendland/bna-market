"""
Unit tests for ETL service
"""

import pytest
import pandas as pd
from unittest.mock import patch, MagicMock, call
from bna_market.services.etl_service import ETLService, run_etl


class TestETLService:
    """Tests for ETLService class"""

    def test_init_with_default_db_path(self):
        """Should initialize with default database path from config"""
        service = ETLService()
        assert service.db_path is not None
        assert service.logger is not None

    def test_init_with_custom_db_path(self):
        """Should initialize with custom database path"""
        custom_path = "/custom/path/db.sqlite"
        service = ETLService(db_path=custom_path)
        assert service.db_path == custom_path

    @patch("bna_market.services.etl_service.fetch_for_sale_properties")
    @patch("bna_market.services.etl_service.get_db_connection")
    @patch("bna_market.services.etl_service.read_table_safely")
    def test_update_sales_table_with_new_data(
        self, mock_read, mock_db_conn, mock_fetch, sample_forsale_df
    ):
        """Should successfully update sales table with new data"""
        mock_fetch.return_value = sample_forsale_df
        mock_read.return_value = pd.DataFrame()  # Empty existing table

        mock_conn = MagicMock()
        mock_db_conn.return_value.__enter__.return_value = mock_conn

        service = ETLService()
        result = service.update_sales_table()

        assert result == 2  # Number of records
        mock_fetch.assert_called_once()
        mock_conn.commit.assert_called()

    @patch("bna_market.services.etl_service.fetch_for_sale_properties")
    def test_update_sales_table_skips_empty_dataframe(self, mock_fetch):
        """Should skip update when pipeline returns empty DataFrame"""
        mock_fetch.return_value = pd.DataFrame()

        service = ETLService()
        result = service.update_sales_table()

        assert result == 0
        mock_fetch.assert_called_once()

    @patch("bna_market.services.etl_service.fetch_rental_properties")
    @patch("bna_market.services.etl_service.get_db_connection")
    @patch("bna_market.services.etl_service.read_table_safely")
    def test_update_rentals_table_with_new_data(
        self, mock_read, mock_db_conn, mock_fetch, sample_rental_df
    ):
        """Should successfully update rentals table"""
        mock_fetch.return_value = sample_rental_df
        mock_read.return_value = pd.DataFrame()

        mock_conn = MagicMock()
        mock_db_conn.return_value.__enter__.return_value = mock_conn

        service = ETLService()
        result = service.update_rentals_table()

        assert result == 2
        mock_fetch.assert_called_once()

    @patch("bna_market.services.etl_service.fetch_rental_properties")
    def test_update_rentals_table_skips_empty_dataframe(self, mock_fetch):
        """Should skip update when pipeline returns empty DataFrame"""
        mock_fetch.return_value = pd.DataFrame()

        service = ETLService()
        result = service.update_rentals_table()

        assert result == 0

    @patch("bna_market.services.etl_service.fetch_fred_metrics")
    @patch("bna_market.services.etl_service.get_db_connection")
    @patch("bna_market.services.etl_service.read_table_safely")
    def test_update_fred_metrics_table(
        self, mock_read, mock_db_conn, mock_fetch, sample_fred_df
    ):
        """Should successfully update FRED metrics table"""
        mock_fetch.return_value = sample_fred_df
        mock_read.return_value = pd.DataFrame()

        mock_conn = MagicMock()
        mock_db_conn.return_value.__enter__.return_value = mock_conn

        service = ETLService()
        result = service.update_fred_metrics_table()

        assert result == 3
        mock_fetch.assert_called_once()

    @patch("bna_market.services.etl_service.fetch_fred_metrics")
    def test_update_fred_table_skips_empty_dataframe(self, mock_fetch):
        """Should skip update when pipeline returns empty DataFrame"""
        mock_fetch.return_value = pd.DataFrame()

        service = ETLService()
        result = service.update_fred_metrics_table()

        assert result == 0

    @patch("bna_market.services.etl_service.fetch_for_sale_properties")
    @patch("bna_market.services.etl_service.get_db_connection")
    @patch("bna_market.services.etl_service.read_table_safely")
    def test_update_sales_deduplicates_on_zpid(
        self, mock_read, mock_db_conn, mock_fetch
    ):
        """Should deduplicate records based on zpid"""
        # Existing data
        existing_df = pd.DataFrame(
            {
                "zpid": [12345],
                "price": [350000],
                "address": ["123 Main"],
                "bedrooms": [3],
                "bathrooms": [2.0],
                "livingArea": [1800],
            }
        )
        mock_read.return_value = existing_df

        # New data with same zpid but updated price
        new_df = pd.DataFrame(
            {
                "zpid": [12345, 67890],
                "price": [360000, 420000],
                "address": ["123 Main", "456 Oak"],
                "bedrooms": [3, 4],
                "bathrooms": [2.0, 3.0],
                "livingArea": [1800, 2200],
            }
        )
        mock_fetch.return_value = new_df

        mock_conn = MagicMock()
        mock_db_conn.return_value.__enter__.return_value = mock_conn

        service = ETLService()
        result = service.update_sales_table()

        # Should have 2 unique zpids (deduplication happened)
        assert result == 2

    @patch.object(ETLService, "update_sales_table")
    @patch.object(ETLService, "update_rentals_table")
    @patch.object(ETLService, "update_fred_metrics_table")
    @patch("bna_market.services.etl_service.validate_environment")
    def test_run_full_refresh(
        self,
        mock_validate,
        mock_fred,
        mock_rentals,
        mock_sales,
    ):
        """Should run all three update methods"""
        mock_sales.return_value = 10
        mock_rentals.return_value = 20
        mock_fred.return_value = 30

        service = ETLService()
        results = service.run_full_refresh()

        assert results["for_sale"] == 10
        assert results["rentals"] == 20
        assert results["fred_metrics"] == 30
        mock_validate.assert_called_once()
        mock_sales.assert_called_once()
        mock_rentals.assert_called_once()
        mock_fred.assert_called_once()


class TestRunETLFunction:
    """Tests for run_etl standalone function"""

    @patch("bna_market.services.etl_service.ETLService")
    def test_run_etl_calls_service(self, mock_service_class):
        """Should create ETLService and call run_full_refresh"""
        mock_service = MagicMock()
        mock_service.run_full_refresh.return_value = {
            "for_sale": 5,
            "rentals": 10,
            "fred_metrics": 15,
        }
        mock_service_class.return_value = mock_service

        result = run_etl()

        assert result == {"for_sale": 5, "rentals": 10, "fred_metrics": 15}
        mock_service_class.assert_called_once()
        mock_service.run_full_refresh.assert_called_once()
