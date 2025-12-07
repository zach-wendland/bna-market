"""Pytest configuration and shared fixtures"""

import pytest
import pandas as pd
import sqlite3
import tempfile
import os
from unittest.mock import MagicMock


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


@pytest.fixture
def temp_db():
    """Temporary SQLite database for testing"""
    fd, db_path = tempfile.mkstemp(suffix=".db")
    # Close the file descriptor immediately on Windows to avoid lock issues
    os.close(fd)

    conn = sqlite3.connect(db_path)

    # Create test tables
    conn.execute(
        """
        CREATE TABLE BNA_FORSALE (
            zpid INTEGER PRIMARY KEY,
            price REAL,
            address TEXT,
            bedrooms INTEGER,
            bathrooms REAL,
            livingArea INTEGER
        )
    """
    )

    conn.execute(
        """
        CREATE TABLE BNA_RENTALS (
            zpid INTEGER PRIMARY KEY,
            price REAL,
            address TEXT,
            bedrooms INTEGER,
            bathrooms REAL,
            livingArea INTEGER
        )
    """
    )

    conn.execute(
        """
        CREATE TABLE BNA_FRED_METRICS (
            date TEXT,
            metric_name TEXT,
            series_id TEXT,
            value REAL,
            PRIMARY KEY (date, series_id)
        )
    """
    )

    conn.commit()
    conn.close()

    yield db_path

    # Clean up - file descriptor already closed above
    try:
        os.unlink(db_path)
    except PermissionError:
        # On Windows, file might still be locked; ignore cleanup failure
        pass


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
    """Flask test client for API testing"""
    from bna_market.web.app import create_app

    app = create_app({"TESTING": True})
    with app.test_client() as client:
        yield client
