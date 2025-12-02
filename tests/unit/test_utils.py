"""Unit tests for utility modules"""

import pytest
import sqlite3
from utils.database import get_db_connection, read_table_safely
from utils.logger import setup_logger
from utils.validators import validate_zillow_property, validate_zillow_dataframe
from utils.retry import retry_with_backoff
from utils.env_validator import validate_environment


class TestDatabase:
    """Tests for database utilities"""

    def test_get_db_connection_returns_connection(self, temp_db, monkeypatch):
        """Should return SQLite connection"""
        monkeypatch.setattr("utils.database.DATABASE_CONFIG", {"path": temp_db})

        with get_db_connection() as conn:
            assert isinstance(conn, sqlite3.Connection)

    def test_read_table_safely_returns_dataframe(self, temp_db):
        """Should return DataFrame for existing table"""
        conn = sqlite3.connect(temp_db)

        result = read_table_safely("BNA_FORSALE", conn)

        assert result is not None
        assert len(result) == 0  # Empty table

    def test_read_table_safely_handles_missing_table(self, temp_db):
        """Should return empty DataFrame for missing table"""
        conn = sqlite3.connect(temp_db)

        result = read_table_safely("NONEXISTENT_TABLE", conn)

        assert result is not None
        assert len(result) == 0


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
        import pandas as pd

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

        @retry_with_backoff(max_retries=3, initial_delay=0.01)
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

        @retry_with_backoff(max_retries=2, initial_delay=0.01)
        def always_fails():
            raise ValueError("Always fails")

        with pytest.raises(ValueError, match="Always fails"):
            always_fails()


class TestEnvValidator:
    """Tests for environment validator"""

    def test_validate_environment_passes_with_keys(self, monkeypatch):
        """Should pass when all required keys present"""
        monkeypatch.setenv("RAPID_API_KEY", "test_key")
        monkeypatch.setenv("FRED_API_KEY", "test_key")

        result = validate_environment()

        assert result is True

    def test_validate_environment_fails_without_keys(self, monkeypatch):
        """Should fail when keys missing"""
        monkeypatch.delenv("RAPID_API_KEY", raising=False)
        monkeypatch.delenv("FRED_API_KEY", raising=False)

        result = validate_environment()

        assert result is False
