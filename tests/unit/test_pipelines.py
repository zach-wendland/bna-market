"""Unit tests for pipeline modules"""

import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from bna_market.pipelines.for_sale import fetch_for_sale_properties
from bna_market.pipelines.rental import fetch_rental_properties
from bna_market.pipelines.fred_metrics import fetch_fred_metrics


class TestForSalePipeline:
    """Tests for for-sale pipeline"""

    @patch("bna_market.pipelines.zillow_base.requests.get")
    def test_forsale_pipe_returns_dataframe(self, mock_get, sample_zillow_response):
        """Should return DataFrame with property data"""
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = sample_zillow_response

        result = fetch_for_sale_properties()

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert "zpid" in result.columns
        assert "price" in result.columns

    @patch("bna_market.pipelines.zillow_base.requests.get")
    def test_forsale_pipe_handles_empty_response(self, mock_get):
        """Should return empty DataFrame on empty API response"""
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"totalResultCount": 0, "results": []}

        result = fetch_for_sale_properties()

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0

    def test_forsale_pipe_requires_api_key(self, monkeypatch):
        """Should raise ValueError if API key missing"""
        # Set env var to empty string (monkeypatch.delenv doesn't work after load_dotenv)
        monkeypatch.setenv("RAPID_API_KEY", "")

        with pytest.raises(ValueError, match="RAPID_API_KEY not found"):
            fetch_for_sale_properties()


class TestRentalPipeline:
    """Tests for rental pipeline"""

    @patch("bna_market.pipelines.zillow_base.requests.get")
    def test_rental_pipe_returns_dataframe(self, mock_get, sample_zillow_response):
        """Should return DataFrame with rental data"""
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = sample_zillow_response

        result = fetch_rental_properties()

        assert isinstance(result, pd.DataFrame)
        assert len(result) >= 0

    def test_rental_pipe_requires_api_key(self, monkeypatch):
        """Should raise ValueError if API key missing"""
        # Set env var to empty string (monkeypatch.delenv doesn't work after load_dotenv)
        monkeypatch.setenv("RAPID_API_KEY", "")

        with pytest.raises(ValueError, match="RAPID_API_KEY not found"):
            fetch_rental_properties()


class TestFredMetricsPipeline:
    """Tests for FRED metrics pipeline"""

    @patch("bna_market.pipelines.fred_metrics.Fred")
    def test_fred_pipe_returns_dataframe(self, mock_fred_class):
        """Should return DataFrame with FRED metrics"""
        mock_fred = MagicMock()
        mock_fred.get_series.return_value = pd.Series(
            [350000, 355000], index=pd.to_datetime(["2024-01-01", "2024-02-01"])
        )
        mock_fred_class.return_value = mock_fred

        result = fetch_fred_metrics()

        assert isinstance(result, pd.DataFrame)
        assert "date" in result.columns
        assert "metric_name" in result.columns
        assert "series_id" in result.columns
        assert "value" in result.columns

    def test_fred_pipe_requires_api_key(self, monkeypatch):
        """Should raise ValueError if API key missing"""
        # Set env var to empty string (monkeypatch.delenv doesn't work after load_dotenv)
        monkeypatch.setenv("FRED_API_KEY", "")

        with pytest.raises(ValueError, match="FRED_API_KEY not found"):
            fetch_fred_metrics()
