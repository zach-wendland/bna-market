"""Pytest configuration and shared fixtures for Supabase-based tests"""

import pytest
import pandas as pd
from unittest.mock import MagicMock, patch
from contextlib import contextmanager


@pytest.fixture
def sample_zillow_response():
    """Sample Zillow API response for testing"""
    return {
        "totalResultCount": 2,
        "props": [
            {
                "zpid": 12345,
                "price": 350000,
                "address": "123 Main St, Nashville, TN 37203",
                "bedrooms": 3,
                "bathrooms": 2.0,
                "livingArea": 1800,
                "propertyType": "SINGLE_FAMILY",
                "latitude": 36.1627,
                "longitude": -86.7816,
                "imgSrc": "https://example.com/img.jpg",
                "detailUrl": "https://zillow.com/homedetails/12345",
                "daysOnZillow": 5,
                "listingStatus": "FOR_SALE",
            },
            {
                "zpid": 67890,
                "price": 425000,
                "address": "456 Oak Ave, Nashville, TN 37215",
                "bedrooms": 4,
                "bathrooms": 3.0,
                "livingArea": 2400,
                "propertyType": "SINGLE_FAMILY",
                "latitude": 36.1447,
                "longitude": -86.8027,
                "imgSrc": "https://example.com/img2.jpg",
                "detailUrl": "https://zillow.com/homedetails/67890",
                "daysOnZillow": 12,
                "listingStatus": "FOR_SALE",
            },
        ],
    }


@pytest.fixture
def sample_forsale_df():
    """Sample for-sale properties DataFrame"""
    return pd.DataFrame(
        {
            "zpid": [12345, 67890],
            "price": [350000, 425000],
            "address": ["123 Main St, Nashville, TN", "456 Oak Ave, Nashville, TN"],
            "bedrooms": [3, 4],
            "bathrooms": [2.0, 3.0],
            "livingArea": [1800, 2400],
        }
    )


@pytest.fixture
def sample_rental_df():
    """Sample rental properties DataFrame"""
    return pd.DataFrame(
        {
            "zpid": [11111, 22222],
            "price": [1800, 2200],
            "address": ["789 Elm St, Nashville, TN", "321 Pine Rd, Nashville, TN"],
            "bedrooms": [2, 3],
            "bathrooms": [1.0, 2.0],
            "livingArea": [900, 1400],
        }
    )


@pytest.fixture
def sample_fred_df():
    """Sample FRED metrics DataFrame"""
    return pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-01", "2024-02-01", "2024-03-01"]),
            "metric_name": ["median_price", "median_price", "median_price"],
            "series_id": ["MEDLISPRI39580", "MEDLISPRI39580", "MEDLISPRI39580"],
            "value": [350000.0, 355000.0, 360000.0],
        }
    )


class MockCursor:
    """Mock database cursor that mimics psycopg2 cursor behavior"""

    def __init__(self, data=None):
        self._data = data or []
        self._description = []
        self._index = 0

    def execute(self, query, params=None):
        """Mock execute - doesn't do anything but stores the query"""
        self._query = query
        self._params = params

    def fetchone(self):
        """Return first row or None"""
        if self._data:
            return self._data[0]
        return None

    def fetchall(self):
        """Return all rows"""
        return self._data

    @property
    def description(self):
        """Return column descriptions"""
        return self._description


class MockConnection:
    """Mock database connection that mimics psycopg2 connection"""

    def __init__(self, cursor_data=None, columns=None):
        self._cursor = MockCursor(cursor_data)
        if columns:
            self._cursor._description = [(col,) for col in columns]

    def cursor(self):
        return self._cursor

    def commit(self):
        pass

    def rollback(self):
        pass

    def close(self):
        pass


@pytest.fixture
def mock_db_connection():
    """
    Mock database connection fixture for API route testing.

    Returns a context manager that yields a MockConnection.
    Configure the mock data by setting mock_db_connection.data and mock_db_connection.columns
    """
    @contextmanager
    def _mock_connection(data=None, columns=None):
        yield MockConnection(data, columns)

    return _mock_connection


@pytest.fixture
def mock_supabase_client():
    """Mock Supabase client for ETL testing"""
    mock = MagicMock()

    # Mock the table().upsert().execute() chain
    mock_table = MagicMock()
    mock_upsert = MagicMock()
    mock_execute = MagicMock()

    mock.table.return_value = mock_table
    mock_table.upsert.return_value = mock_upsert
    mock_upsert.execute.return_value = MagicMock(data=[{"id": 1}])

    return mock


@pytest.fixture
def mock_requests_get(sample_zillow_response):
    """Mock requests.get for API calls"""
    mock = MagicMock()
    mock.return_value.status_code = 200
    mock.return_value.json.return_value = sample_zillow_response
    return mock


@pytest.fixture
def mock_fred_api():
    """Mock FRED API client"""
    mock = MagicMock()
    mock.get_series.return_value = pd.Series(
        [350000, 355000, 360000],
        index=pd.to_datetime(["2024-01-01", "2024-02-01", "2024-03-01"]),
    )
    return mock


@pytest.fixture
def flask_test_client():
    """
    Flask test client for API testing with mocked database.

    The database connections are mocked to return sample data.
    """
    from bna_market.web.app import create_app

    app = create_app({"TESTING": True})

    # Sample data for the mock cursor
    sample_forsale = [
        (12345, "123 Main St, Nashville, TN", 350000, 3, 2.0, 1800,
         "SINGLE_FAMILY", 36.1627, -86.7816, "https://example.com/img.jpg",
         "/homedetails/12345", 5, "FOR_SALE"),
        (67890, "456 Oak Ave, Nashville, TN", 425000, 4, 3.0, 2400,
         "SINGLE_FAMILY", 36.1447, -86.8027, "https://example.com/img2.jpg",
         "/homedetails/67890", 12, "FOR_SALE"),
    ]

    sample_rentals = [
        (11111, "789 Elm St, Nashville, TN", 1800, 2, 1.0, 900,
         "APARTMENT", 36.1500, -86.7900, "https://example.com/rental1.jpg",
         "/homedetails/11111", 3, "FOR_RENT"),
        (22222, "321 Pine Rd, Nashville, TN", 2200, 3, 2.0, 1400,
         "TOWNHOUSE", 36.1600, -86.7800, "https://example.com/rental2.jpg",
         "/homedetails/22222", 7, "FOR_RENT"),
    ]

    sample_fred = [
        ("2024-03-01", "median_price", "MEDLISPRI39580", 360000.0),
        ("2024-02-01", "median_price", "MEDLISPRI39580", 355000.0),
        ("2024-01-01", "median_price", "MEDLISPRI39580", 350000.0),
    ]

    columns_properties = [
        "zpid", "address", "price", "bedrooms", "bathrooms", "livingArea",
        "propertyType", "latitude", "longitude", "imgSrc", "detailUrl",
        "daysOnZillow", "listingStatus"
    ]

    columns_fred = ["date", "metricName", "seriesId", "value"]

    # Create a mock that handles different queries
    class SmartMockCursor:
        def __init__(self):
            self._data = []
            self._description = []

        def execute(self, query, params=None):
            query_lower = query.lower()
            if "count(*)" in query_lower:
                if "bna_rentals" in query_lower:
                    self._data = [(2, 2000)]  # count, avg
                else:
                    self._data = [(2, 387500)]  # count, avg
                self._description = [("count",), ("avg_price",)]
            elif "bna_rentals" in query_lower and "select" in query_lower:
                self._data = sample_rentals
                self._description = [(col,) for col in columns_properties]
            elif "bna_forsale" in query_lower and "select" in query_lower:
                self._data = sample_forsale
                self._description = [(col,) for col in columns_properties]
            elif "bna_fred_metrics" in query_lower and "select" in query_lower:
                self._data = sample_fred
                self._description = [(col,) for col in columns_fred]
            else:
                self._data = []
                self._description = []

        def fetchone(self):
            return self._data[0] if self._data else None

        def fetchall(self):
            return self._data

        @property
        def description(self):
            return self._description

    class SmartMockConnection:
        def cursor(self):
            return SmartMockCursor()

        def commit(self):
            pass

        def rollback(self):
            pass

        def close(self):
            pass

    @contextmanager
    def mock_get_db_connection():
        yield SmartMockConnection()

    # Patch the database connection
    with patch("bna_market.web.api.routes.get_db_connection", mock_get_db_connection):
        with patch("bna_market.utils.database.get_db_connection", mock_get_db_connection):
            with app.test_client() as client:
                yield client
