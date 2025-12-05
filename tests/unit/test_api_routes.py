"""Comprehensive unit tests for API routes"""

import pytest
import json
from unittest.mock import patch, MagicMock
from bna_market.web.app import create_app


@pytest.fixture
def app():
    """Create and configure test app"""
    app = create_app({"TESTING": True})
    return app


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


class TestHealthEndpoint:
    """Tests for /api/health endpoint"""

    def test_health_check_returns_200(self, client):
        """Should return 200 OK status"""
        response = client.get("/api/health")
        assert response.status_code == 200

    def test_health_check_returns_json(self, client):
        """Should return JSON response"""
        response = client.get("/api/health")
        assert response.content_type == "application/json"

    def test_health_check_contains_status(self, client):
        """Should contain status field"""
        response = client.get("/api/health")
        data = response.get_json()
        assert "status" in data
        assert data["status"] == "healthy"

    def test_health_check_contains_endpoints(self, client):
        """Should list available endpoints"""
        response = client.get("/api/health")
        data = response.get_json()
        assert "endpoints" in data
        assert "/api/health" in data["endpoints"]
        assert "/api/properties/search" in data["endpoints"]
        assert "/api/properties/export" in data["endpoints"]
        assert "/api/metrics/fred" in data["endpoints"]


class TestPropertiesSearchEndpoint:
    """Tests for /api/properties/search endpoint"""

    @patch("bna_market.web.api.routes.get_db_connection")
    def test_search_requires_property_type(self, mock_db, client):
        """Should return 400 if property_type missing"""
        response = client.get("/api/properties/search")
        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data

    @patch("bna_market.web.api.routes.get_db_connection")
    def test_search_validates_property_type(self, mock_db, client):
        """Should return 400 for invalid property_type"""
        response = client.get("/api/properties/search?property_type=invalid")
        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data
        assert "forsale" in data["error"]
        assert "rental" in data["error"]

    @patch("bna_market.web.api.routes.get_db_connection")
    def test_search_accepts_forsale_property_type(self, mock_db_conn, client):
        """Should accept 'forsale' property_type"""
        # Setup mock
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (5,)  # Total count
        mock_cursor.fetchall.return_value = []
        mock_cursor.description = [
            ("zpid",), ("address",), ("price",), ("bedrooms",),
            ("bathrooms",), ("livingArea",), ("propertyType",),
            ("latitude",), ("longitude",), ("imgSrc",),
            ("detailUrl",), ("daysOnZillow",), ("listingStatus",)
        ]
        mock_conn.cursor.return_value = mock_cursor
        mock_db_conn.return_value.__enter__.return_value = mock_conn

        response = client.get("/api/properties/search?property_type=forsale")
        assert response.status_code == 200

    @patch("bna_market.web.api.routes.get_db_connection")
    def test_search_accepts_rental_property_type(self, mock_db_conn, client):
        """Should accept 'rental' property_type"""
        # Setup mock
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (3,)
        mock_cursor.fetchall.return_value = []
        mock_cursor.description = [
            ("zpid",), ("address",), ("price",), ("bedrooms",),
            ("bathrooms",), ("livingArea",), ("propertyType",),
            ("latitude",), ("longitude",), ("imgSrc",),
            ("detailUrl",), ("daysOnZillow",), ("listingStatus",)
        ]
        mock_conn.cursor.return_value = mock_cursor
        mock_db_conn.return_value.__enter__.return_value = mock_conn

        response = client.get("/api/properties/search?property_type=rental")
        assert response.status_code == 200

    @patch("bna_market.web.api.routes.get_db_connection")
    def test_search_returns_pagination_metadata(self, mock_db_conn, client):
        """Should return pagination information"""
        # Setup mock
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (50,)  # Total count
        mock_cursor.fetchall.return_value = []
        mock_cursor.description = [
            ("zpid",), ("address",), ("price",), ("bedrooms",),
            ("bathrooms",), ("livingArea",), ("propertyType",),
            ("latitude",), ("longitude",), ("imgSrc",),
            ("detailUrl",), ("daysOnZillow",), ("listingStatus",)
        ]
        mock_conn.cursor.return_value = mock_cursor
        mock_db_conn.return_value.__enter__.return_value = mock_conn

        response = client.get("/api/properties/search?property_type=forsale")
        data = response.get_json()

        assert "pagination" in data
        assert "page" in data["pagination"]
        assert "per_page" in data["pagination"]
        assert "total_count" in data["pagination"]
        assert "total_pages" in data["pagination"]
        assert "has_next" in data["pagination"]
        assert "has_prev" in data["pagination"]

    @patch("bna_market.web.api.routes.get_db_connection")
    def test_search_applies_price_filters(self, mock_db_conn, client):
        """Should apply price filters correctly"""
        # Setup mock
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (10,)
        mock_cursor.fetchall.return_value = []
        mock_cursor.description = [
            ("zpid",), ("address",), ("price",), ("bedrooms",),
            ("bathrooms",), ("livingArea",), ("propertyType",),
            ("latitude",), ("longitude",), ("imgSrc",),
            ("detailUrl",), ("daysOnZillow",), ("listingStatus",)
        ]
        mock_conn.cursor.return_value = mock_cursor
        mock_db_conn.return_value.__enter__.return_value = mock_conn

        response = client.get("/api/properties/search?property_type=forsale&min_price=200000&max_price=500000")
        assert response.status_code == 200

        # Check that execute was called with price parameters
        calls = mock_cursor.execute.call_args_list
        assert len(calls) >= 2  # Count query + data query

        # Verify price conditions in SQL
        count_query = calls[0][0][0]
        assert "price >= ?" in count_query
        assert "price <= ?" in count_query


class TestPropertiesExportEndpoint:
    """Tests for /api/properties/export endpoint"""

    @patch("bna_market.web.api.routes.get_db_connection")
    def test_export_requires_property_type(self, mock_db, client):
        """Should return 400 if property_type missing"""
        response = client.get("/api/properties/export")
        assert response.status_code == 400

    @patch("bna_market.web.api.routes.get_db_connection")
    def test_export_returns_csv(self, mock_db_conn, client):
        """Should return CSV file"""
        # Setup mock
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            (123, "123 Main St", 350000, 3, 2, 1800, "SINGLE_FAMILY", 36.1, -86.8, "img.jpg", "url", 30, "FOR_SALE")
        ]
        mock_cursor.description = [
            ("zpid",), ("address",), ("price",), ("bedrooms",),
            ("bathrooms",), ("livingArea",), ("propertyType",),
            ("latitude",), ("longitude",), ("daysOnZillow",),
            ("listingStatus",), ("detailUrl",)
        ]
        mock_conn.cursor.return_value = mock_cursor
        mock_db_conn.return_value.__enter__.return_value = mock_conn

        response = client.get("/api/properties/export?property_type=forsale")
        assert response.status_code == 200
        assert response.content_type == "text/csv"
        assert "attachment" in response.headers.get("Content-Disposition", "")

    @patch("bna_market.web.api.routes.get_db_connection")
    def test_export_filename_includes_property_type(self, mock_db_conn, client):
        """Should include property type in filename"""
        # Setup mock
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_cursor.description = [("zpid",)]
        mock_conn.cursor.return_value = mock_cursor
        mock_db_conn.return_value.__enter__.return_value = mock_conn

        response = client.get("/api/properties/export?property_type=rental")
        assert "bna_rental_export.csv" in response.headers.get("Content-Disposition", "")


class TestFredMetricsEndpoint:
    """Tests for /api/metrics/fred endpoint"""

    @patch("bna_market.web.api.routes.get_db_connection")
    def test_fred_metrics_returns_200(self, mock_db_conn, client):
        """Should return 200 OK"""
        # Setup mock
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_cursor.description = [("date",), ("metric_name",), ("series_id",), ("value",)]
        mock_conn.cursor.return_value = mock_cursor
        mock_db_conn.return_value.__enter__.return_value = mock_conn

        response = client.get("/api/metrics/fred")
        assert response.status_code == 200

    @patch("bna_market.web.api.routes.get_db_connection")
    def test_fred_metrics_returns_metrics_array(self, mock_db_conn, client):
        """Should return metrics array"""
        # Setup mock
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            ("2024-01-01", "median_price", "SERIES123", 350000),
            ("2024-02-01", "median_price", "SERIES123", 355000),
        ]
        mock_cursor.description = [("date",), ("metric_name",), ("series_id",), ("value",)]
        mock_conn.cursor.return_value = mock_cursor
        mock_db_conn.return_value.__enter__.return_value = mock_conn

        response = client.get("/api/metrics/fred")
        data = response.get_json()

        assert "metrics" in data
        assert "count" in data
        assert isinstance(data["metrics"], list)
        assert data["count"] == 2

    @patch("bna_market.web.api.routes.get_db_connection")
    def test_fred_metrics_accepts_filters(self, mock_db_conn, client):
        """Should accept filter parameters"""
        # Setup mock
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_cursor.description = [("date",), ("metric_name",), ("series_id",), ("value",)]
        mock_conn.cursor.return_value = mock_cursor
        mock_db_conn.return_value.__enter__.return_value = mock_conn

        response = client.get("/api/metrics/fred?metric_name=median_price&start_date=2024-01-01&end_date=2024-12-31")
        assert response.status_code == 200

        # Verify filters were applied
        calls = mock_cursor.execute.call_args_list
        query = calls[0][0][0]
        assert "metric_name = ?" in query
        assert "date >= ?" in query
        assert "date <= ?" in query


class TestTableNameSecurityMapping:
    """Tests for SQL injection prevention via table name mapping"""

    @patch("bna_market.web.api.routes.get_db_connection")
    def test_search_uses_mapping_for_forsale(self, mock_db_conn, client):
        """Should use PROPERTY_TYPE_TABLE_MAP for forsale"""
        # Setup mock
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (0,)
        mock_cursor.fetchall.return_value = []
        mock_cursor.description = [("zpid",)]
        mock_conn.cursor.return_value = mock_cursor
        mock_db_conn.return_value.__enter__.return_value = mock_conn

        response = client.get("/api/properties/search?property_type=forsale")

        # Verify BNA_FORSALE table was used
        calls = mock_cursor.execute.call_args_list
        count_query = calls[0][0][0]
        assert "BNA_FORSALE" in count_query

    @patch("bna_market.web.api.routes.get_db_connection")
    def test_search_uses_mapping_for_rental(self, mock_db_conn, client):
        """Should use PROPERTY_TYPE_TABLE_MAP for rental"""
        # Setup mock
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (0,)
        mock_cursor.fetchall.return_value = []
        mock_cursor.description = [("zpid",)]
        mock_conn.cursor.return_value = mock_cursor
        mock_db_conn.return_value.__enter__.return_value = mock_conn

        response = client.get("/api/properties/search?property_type=rental")

        # Verify BNA_RENTALS table was used
        calls = mock_cursor.execute.call_args_list
        count_query = calls[0][0][0]
        assert "BNA_RENTALS" in count_query

    @patch("bna_market.web.api.routes.get_db_connection")
    def test_search_rejects_sql_injection_attempt(self, mock_db, client):
        """Should reject SQL injection attempts in property_type"""
        response = client.get("/api/properties/search?property_type=forsale'; DROP TABLE users; --")
        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data
