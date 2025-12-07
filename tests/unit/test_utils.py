"""Unit tests for utility modules"""

import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from contextlib import contextmanager

from bna_market.utils.database import read_table_safely, VALID_TABLE_NAMES
from bna_market.utils.logger import setup_logger
from bna_market.utils.validators import validate_zillow_property, validate_zillow_dataframe
from bna_market.utils.retry import retry_with_backoff
from bna_market.utils.env_validator import validate_environment


class TestDatabase:
    """Tests for database utilities"""

    def test_read_table_safely_returns_dataframe(self):
        """Should return DataFrame for existing table"""
        # Mock the connection to return empty DataFrame
        mock_conn = MagicMock()

        with patch("bna_market.utils.database.pd.read_sql") as mock_read_sql:
            mock_read_sql.return_value = pd.DataFrame({"zpid": [], "price": []})

            result = read_table_safely("bna_forsale", mock_conn)

            assert result is not None
            assert isinstance(result, pd.DataFrame)
            mock_read_sql.assert_called_once()

    def test_read_table_safely_normalizes_table_name(self):
        """Should normalize table names to lowercase"""
        mock_conn = MagicMock()

        with patch("bna_market.utils.database.pd.read_sql") as mock_read_sql:
            mock_read_sql.return_value = pd.DataFrame()

            # Pass uppercase table name - should be normalized
            result = read_table_safely("BNA_FORSALE", mock_conn)

            # Check that the query uses lowercase
            call_args = mock_read_sql.call_args
            assert "bna_forsale" in call_args[0][0]

    def test_read_table_safely_rejects_invalid_table_name(self):
        """Should raise ValueError for table names not in whitelist"""
        mock_conn = MagicMock()

        with pytest.raises(ValueError, match="Invalid table name"):
            read_table_safely("NONEXISTENT_TABLE", mock_conn)

    def test_valid_table_names_whitelist(self):
        """Should have correct valid table names"""
        assert "bna_forsale" in VALID_TABLE_NAMES
        assert "bna_rentals" in VALID_TABLE_NAMES
        assert "bna_fred_metrics" in VALID_TABLE_NAMES


class TestLogger:
    """Tests for logger utilities"""

    def test_setup_logger_returns_logger(self):
        """Should return configured logger"""
        logger = setup_logger("test")

        assert logger is not None
        assert logger.name == "test"


class TestValidators:
    """Tests for validation utilities"""

    def test_validate_zillow_property_accepts_valid(self):
        """Should accept valid property"""
        prop = {"zpid": 12345, "price": 350000, "address": "123 Main St"}
        assert validate_zillow_property(prop) is True

    def test_validate_zillow_property_rejects_missing_zpid(self):
        """Should reject property without zpid"""
        prop = {"price": 350000, "address": "123 Main St"}
        assert validate_zillow_property(prop) is False

    def test_validate_zillow_property_rejects_missing_price(self):
        """Should reject property without price"""
        prop = {"zpid": 12345, "address": "123 Main St"}
        assert validate_zillow_property(prop) is False

    def test_validate_dataframe_returns_dataframe(self):
        """Should return DataFrame after validation"""
        df = pd.DataFrame(
            {"zpid": [12345], "price": [350000], "address": ["123 Main St"]}
        )
        result = validate_zillow_dataframe(df, "forSale")
        assert isinstance(result, pd.DataFrame)


class TestRetry:
    """Tests for retry utilities"""

    def test_retry_succeeds_on_first_attempt(self):
        """Should succeed without retry if function works"""
        call_count = [0]

        @retry_with_backoff(max_retries=3)
        def success_func():
            call_count[0] += 1
            return "success"

        result = success_func()

        assert result == "success"
        assert call_count[0] == 1

    def test_retry_eventually_succeeds(self):
        """Should retry until success"""
        call_count = [0]

        @retry_with_backoff(max_retries=3, base_delay=0.01)
        def flaky_func():
            call_count[0] += 1
            if call_count[0] < 3:
                raise ConnectionError("Temporary failure")
            return "success"

        result = flaky_func()

        assert result == "success"
        assert call_count[0] == 3

    def test_retry_fails_after_max_attempts(self):
        """Should raise exception after max retries"""

        @retry_with_backoff(max_retries=2, base_delay=0.01)
        def always_fails():
            raise ValueError("Always fails")

        with pytest.raises(ValueError, match="Always fails"):
            always_fails()


class TestEnvValidator:
    """Tests for environment validator"""

    def test_validate_environment_passes_with_all_keys(self, monkeypatch):
        """Should pass when all required keys present"""
        monkeypatch.setenv("RAPID_API_KEY", "test_key")
        monkeypatch.setenv("FRED_API_KEY", "test_key")
        monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
        monkeypatch.setenv("SUPABASE_SERVICE_KEY", "test_service_key")

        result = validate_environment(reload_dotenv=False)

        assert result is True

    def test_validate_environment_fails_without_keys(self, monkeypatch):
        """Should fail when keys missing"""
        monkeypatch.delenv("RAPID_API_KEY", raising=False)
        monkeypatch.delenv("FRED_API_KEY", raising=False)
        monkeypatch.delenv("SUPABASE_URL", raising=False)
        monkeypatch.delenv("SUPABASE_SERVICE_KEY", raising=False)

        # Pass reload_dotenv=False to prevent re-reading .env file
        result = validate_environment(reload_dotenv=False)

        assert result is False
