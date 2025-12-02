"""Unit tests for pipeline modules"""

import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from pipelines.forSale import forSalePipe01
from pipelines.rentalPipe import rentalPipe01
from pipelines.otherMetricsPipe import fredMetricsPipe01


class TestForSalePipeline:
    """Tests for for-sale pipeline"""

    @patch("pipelines.zillow_base.requests.get")
    def test_forsale_pipe_returns_dataframe(self, mock_get, sample_zillow_response):
        """Should return DataFrame with property data"""
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = sample_zillow_response

        result = forSalePipe01()

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert "zpid" in result.columns
        assert "price" in result.columns

    @patch("pipelines.zillow_base.requests.get")
    def test_forsale_pipe_handles_empty_response(self, mock_get):
        """Should return empty DataFrame on empty API response"""
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"totalResultCount": 0, "results": []}

        result = forSalePipe01()

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0

    def test_forsale_pipe_requires_api_key(self, monkeypatch):
        """Should raise ValueError if API key missing"""
        monkeypatch.delenv("RAPID_API_KEY", raising=False)

        with pytest.raises(ValueError, match="RAPID_API_KEY not found"):
            forSalePipe01()


class TestRentalPipeline:
    """Tests for rental pipeline"""

    @patch("pipelines.zillow_base.requests.get")
    def test_rental_pipe_returns_dataframe(self, mock_get, sample_zillow_response):
        """Should return DataFrame with rental data"""
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = sample_zillow_response

        result = rentalPipe01()

        assert isinstance(result, pd.DataFrame)
        assert len(result) >= 0

    def test_rental_pipe_requires_api_key(self, monkeypatch):
        """Should raise ValueError if API key missing"""
        monkeypatch.delenv("RAPID_API_KEY", raising=False)

        with pytest.raises(ValueError, match="RAPID_API_KEY not found"):
            rentalPipe01()


class TestFredMetricsPipeline:
    """Tests for FRED metrics pipeline"""

    @patch("pipelines.otherMetricsPipe.Fred")
    def test_fred_pipe_returns_dataframe(self, mock_fred_class):
        """Should return DataFrame with FRED metrics"""
        mock_fred = MagicMock()
        mock_fred.get_series.return_value = pd.Series(
            [350000, 355000], index=pd.to_datetime(["2024-01-01", "2024-02-01"])
        )
        mock_fred_class.return_value = mock_fred

        result = fredMetricsPipe01()

        assert isinstance(result, pd.DataFrame)
        assert "date" in result.columns
        assert "metric_name" in result.columns
        assert "series_id" in result.columns
        assert "value" in result.columns

    def test_fred_pipe_requires_api_key(self, monkeypatch):
        """Should raise ValueError if API key missing"""
        monkeypatch.delenv("FRED_API_KEY", raising=False)

        with pytest.raises(ValueError, match="FRED_API_KEY not found"):
            fredMetricsPipe01()
