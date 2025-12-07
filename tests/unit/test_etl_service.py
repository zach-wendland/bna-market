"""
Unit tests for ETL service with Supabase
"""

import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from bna_market.services.etl_service import ETLService, run_etl


class TestETLService:
    """Tests for ETLService class"""

    def test_init_creates_logger(self):
        """Should initialize with logger"""
        service = ETLService()
        assert service.logger is not None

    def test_prepare_dataframe_handles_empty(self):
        """Should return empty DataFrame unchanged"""
        service = ETLService()
        df = pd.DataFrame()
        result = service._prepare_dataframe(df)
        assert result.empty

    def test_prepare_dataframe_converts_dicts_to_json(self):
        """Should convert dict columns to JSON strings"""
        service = ETLService()
        df = pd.DataFrame({
            "id": [1],
            "data": [{"key": "value"}]
        })
        result = service._prepare_dataframe(df)
        assert result["data"].iloc[0] == '{"key": "value"}'

    def test_prepare_dataframe_replaces_nan_with_none(self):
        """Should replace NaN with None for PostgreSQL"""
        service = ETLService()
        df = pd.DataFrame({
            "id": [1, 2],
            "value": [100, float("nan")]
        })
        result = service._prepare_dataframe(df)
        # pd.where replaces NaN with None, check using isnull
        assert pd.isnull(result["value"].iloc[1])

    @patch("bna_market.services.etl_service.fetch_for_sale_properties")
    @patch("bna_market.services.etl_service.upsert_dataframe")
    def test_update_sales_table_with_new_data(
        self, mock_upsert, mock_fetch, sample_forsale_df
    ):
        """Should successfully update sales table with new data"""
        mock_fetch.return_value = sample_forsale_df
        mock_upsert.return_value = 2

        service = ETLService()
        result = service.update_sales_table()

        assert result == 2
        mock_fetch.assert_called_once()
        mock_upsert.assert_called_once()
        # Verify table name
        call_args = mock_upsert.call_args
        assert call_args.kwargs["table_name"] == "bna_forsale"

    @patch("bna_market.services.etl_service.fetch_for_sale_properties")
    def test_update_sales_table_skips_empty_dataframe(self, mock_fetch):
        """Should skip update when pipeline returns empty DataFrame"""
        mock_fetch.return_value = pd.DataFrame()

        service = ETLService()
        result = service.update_sales_table()

        assert result == 0
        mock_fetch.assert_called_once()

    @patch("bna_market.services.etl_service.fetch_rental_properties")
    @patch("bna_market.services.etl_service.upsert_dataframe")
    def test_update_rentals_table_with_new_data(
        self, mock_upsert, mock_fetch, sample_rental_df
    ):
        """Should successfully update rentals table"""
        mock_fetch.return_value = sample_rental_df
        mock_upsert.return_value = 2

        service = ETLService()
        result = service.update_rentals_table()

        assert result == 2
        mock_fetch.assert_called_once()
        mock_upsert.assert_called_once()
        # Verify table name
        call_args = mock_upsert.call_args
        assert call_args.kwargs["table_name"] == "bna_rentals"

    @patch("bna_market.services.etl_service.fetch_rental_properties")
    def test_update_rentals_table_skips_empty_dataframe(self, mock_fetch):
        """Should skip update when pipeline returns empty DataFrame"""
        mock_fetch.return_value = pd.DataFrame()

        service = ETLService()
        result = service.update_rentals_table()

        assert result == 0

    @patch("bna_market.services.etl_service.fetch_fred_metrics")
    @patch("bna_market.services.etl_service.upsert_dataframe")
    def test_update_fred_metrics_table(
        self, mock_upsert, mock_fetch, sample_fred_df
    ):
        """Should successfully update FRED metrics table"""
        mock_fetch.return_value = sample_fred_df
        mock_upsert.return_value = 3

        service = ETLService()
        result = service.update_fred_metrics_table()

        assert result == 3
        mock_fetch.assert_called_once()
        mock_upsert.assert_called_once()
        # Verify table name
        call_args = mock_upsert.call_args
        assert call_args.kwargs["table_name"] == "bna_fred_metrics"

    @patch("bna_market.services.etl_service.fetch_fred_metrics")
    def test_update_fred_table_skips_empty_dataframe(self, mock_fetch):
        """Should skip update when pipeline returns empty DataFrame"""
        mock_fetch.return_value = pd.DataFrame()

        service = ETLService()
        result = service.update_fred_metrics_table()

        assert result == 0

    @patch("bna_market.services.etl_service.fetch_for_sale_properties")
    @patch("bna_market.services.etl_service.upsert_dataframe")
    def test_update_sales_uses_correct_unique_columns(
        self, mock_upsert, mock_fetch
    ):
        """Should use zpid as unique column for deduplication"""
        mock_fetch.return_value = pd.DataFrame({
            "zpid": [12345, 67890],
            "price": [350000, 420000],
            "address": ["123 Main", "456 Oak"],
            "bedrooms": [3, 4],
            "bathrooms": [2.0, 3.0],
            "livingArea": [1800, 2200],
        })
        mock_upsert.return_value = 2

        service = ETLService()
        service.update_sales_table()

        call_args = mock_upsert.call_args
        assert "zpid" in call_args.kwargs["unique_columns"]

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
        mock_validate.return_value = True
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

    @patch("bna_market.services.etl_service.validate_environment")
    def test_run_full_refresh_exits_on_invalid_env(self, mock_validate):
        """Should raise SystemExit when environment validation fails"""
        mock_validate.return_value = False

        service = ETLService()

        with pytest.raises(SystemExit):
            service.run_full_refresh()


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
