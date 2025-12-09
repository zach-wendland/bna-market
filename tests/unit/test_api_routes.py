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
            ("bathrooms",), ("living_area",), ("property_type",),
            ("latitude",), ("longitude",), ("img_src",),
            ("detail_url",), ("days_on_zillow",), ("listing_status",)
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
            ("bathrooms",), ("living_area",), ("property_type",),
            ("latitude",), ("longitude",), ("img_src",),
            ("detail_url",), ("days_on_zillow",), ("listing_status",)
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
            ("bathrooms",), ("living_area",), ("property_type",),
            ("latitude",), ("longitude",), ("img_src",),
            ("detail_url",), ("days_on_zillow",), ("listing_status",)
        ]
        mock_conn.cursor.return_value = mock_cursor
        mock_db_conn.return_value.__enter__.return_value = mock_conn

        response = client.get("/api/properties/search?property_type=forsale")
        data = response.get_json()

        assert "pagination" in data
        assert "page" in data["pagination"]
        assert "perPage" in data["pagination"]
        assert "totalCount" in data["pagination"]
        assert "totalPages" in data["pagination"]
        assert "hasNext" in data["pagination"]
        assert "hasPrev" in data["pagination"]

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
            ("bathrooms",), ("living_area",), ("property_type",),
            ("latitude",), ("longitude",), ("img_src",),
            ("detail_url",), ("days_on_zillow",), ("listing_status",)
        ]
        mock_conn.cursor.return_value = mock_cursor
        mock_db_conn.return_value.__enter__.return_value = mock_conn

        response = client.get("/api/properties/search?property_type=forsale&min_price=200000&max_price=500000")
        assert response.status_code == 200

        # Check that execute was called with price parameters
        calls = mock_cursor.execute.call_args_list
        assert len(calls) >= 2  # Count query + data query

        # Verify price conditions in SQL (PostgreSQL uses %s placeholders)
        count_query = calls[0][0][0]
        assert "price >= %s" in count_query
        assert "price <= %s" in count_query


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
            ("bathrooms",), ("living_area",), ("property_type",),
            ("latitude",), ("longitude",), ("days_on_zillow",),
            ("listing_status",), ("detail_url",)
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
        assert "metric_name = %s" in query
        assert "date >= %s" in query
        assert "date <= %s" in query


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

        # Verify bna_forsale table was used (lowercase for PostgreSQL)
        calls = mock_cursor.execute.call_args_list
        count_query = calls[0][0][0]
        assert "bna_forsale" in count_query

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

        # Verify bna_rentals table was used (lowercase for PostgreSQL)
        calls = mock_cursor.execute.call_args_list
        count_query = calls[0][0][0]
        assert "bna_rentals" in count_query

    @patch("bna_market.web.api.routes.get_db_connection")
    def test_search_rejects_sql_injection_attempt(self, mock_db, client):
        """Should reject SQL injection attempts in property_type"""
        response = client.get("/api/properties/search?property_type=forsale'; DROP TABLE users; --")
        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data


class TestSearchFiltersComprehensive:
    """Additional tests for search filter coverage"""

    @patch("bna_market.web.api.routes.get_app_db_connection")
    def test_search_applies_bedroom_filters(self, mock_db_conn, client):
        """Should apply bedroom filters correctly"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (5,)
        mock_cursor.fetchall.return_value = []
        mock_cursor.description = [
            ("zpid",), ("address",), ("price",), ("bedrooms",),
            ("bathrooms",), ("living_area",), ("property_type",),
            ("latitude",), ("longitude",), ("img_src",),
            ("detail_url",), ("days_on_zillow",), ("listing_status",)
        ]
        mock_conn.cursor.return_value = mock_cursor
        mock_db_conn.return_value.__enter__.return_value = mock_conn

        response = client.get("/api/properties/search?property_type=forsale&min_beds=2&max_beds=4")
        assert response.status_code == 200

        calls = mock_cursor.execute.call_args_list
        count_query = calls[0][0][0]
        assert "bedrooms >= %s" in count_query
        assert "bedrooms <= %s" in count_query

    @patch("bna_market.web.api.routes.get_app_db_connection")
    def test_search_applies_bathroom_filters(self, mock_db_conn, client):
        """Should apply bathroom filters correctly"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (3,)
        mock_cursor.fetchall.return_value = []
        mock_cursor.description = [
            ("zpid",), ("address",), ("price",), ("bedrooms",),
            ("bathrooms",), ("living_area",), ("property_type",),
            ("latitude",), ("longitude",), ("img_src",),
            ("detail_url",), ("days_on_zillow",), ("listing_status",)
        ]
        mock_conn.cursor.return_value = mock_cursor
        mock_db_conn.return_value.__enter__.return_value = mock_conn

        response = client.get("/api/properties/search?property_type=rental&min_baths=1&max_baths=3")
        assert response.status_code == 200

        calls = mock_cursor.execute.call_args_list
        count_query = calls[0][0][0]
        assert "bathrooms >= %s" in count_query
        assert "bathrooms <= %s" in count_query

    @patch("bna_market.web.api.routes.get_app_db_connection")
    def test_search_applies_sqft_filters(self, mock_db_conn, client):
        """Should apply square footage filters correctly"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (2,)
        mock_cursor.fetchall.return_value = []
        mock_cursor.description = [
            ("zpid",), ("address",), ("price",), ("bedrooms",),
            ("bathrooms",), ("living_area",), ("property_type",),
            ("latitude",), ("longitude",), ("img_src",),
            ("detail_url",), ("days_on_zillow",), ("listing_status",)
        ]
        mock_conn.cursor.return_value = mock_cursor
        mock_db_conn.return_value.__enter__.return_value = mock_conn

        response = client.get("/api/properties/search?property_type=forsale&min_sqft=1000&max_sqft=3000")
        assert response.status_code == 200

        calls = mock_cursor.execute.call_args_list
        count_query = calls[0][0][0]
        assert "living_area >= %s" in count_query
        assert "living_area <= %s" in count_query

    @patch("bna_market.web.api.routes.get_app_db_connection")
    def test_search_applies_city_filter(self, mock_db_conn, client):
        """Should apply city filter correctly"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (10,)
        mock_cursor.fetchall.return_value = []
        mock_cursor.description = [
            ("zpid",), ("address",), ("price",), ("bedrooms",),
            ("bathrooms",), ("living_area",), ("property_type",),
            ("latitude",), ("longitude",), ("img_src",),
            ("detail_url",), ("days_on_zillow",), ("listing_status",)
        ]
        mock_conn.cursor.return_value = mock_cursor
        mock_db_conn.return_value.__enter__.return_value = mock_conn

        response = client.get("/api/properties/search?property_type=forsale&city=Nashville")
        assert response.status_code == 200

        calls = mock_cursor.execute.call_args_list
        count_query = calls[0][0][0]
        assert "LOWER(address) LIKE %s" in count_query

    @patch("bna_market.web.api.routes.get_app_db_connection")
    def test_search_applies_zipcode_filter(self, mock_db_conn, client):
        """Should apply ZIP code filter correctly"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (4,)
        mock_cursor.fetchall.return_value = []
        mock_cursor.description = [
            ("zpid",), ("address",), ("price",), ("bedrooms",),
            ("bathrooms",), ("living_area",), ("property_type",),
            ("latitude",), ("longitude",), ("img_src",),
            ("detail_url",), ("days_on_zillow",), ("listing_status",)
        ]
        mock_conn.cursor.return_value = mock_cursor
        mock_db_conn.return_value.__enter__.return_value = mock_conn

        response = client.get("/api/properties/search?property_type=forsale&zip_code=37201")
        assert response.status_code == 200

        calls = mock_cursor.execute.call_args_list
        count_query = calls[0][0][0]
        assert "address LIKE %s" in count_query

    @patch("bna_market.web.api.routes.get_app_db_connection")
    def test_search_returns_properties_with_price_per_sqft(self, mock_db_conn, client):
        """Should calculate pricePerSqft for properties with valid data"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (1,)
        mock_cursor.fetchall.return_value = [
            (123, "123 Main St", 300000, 3, 2, 1500, "SINGLE_FAMILY",
             36.1, -86.8, "img.jpg", "/homedetails/123", 10, "FOR_SALE")
        ]
        mock_cursor.description = [
            ("zpid",), ("address",), ("price",), ("bedrooms",),
            ("bathrooms",), ("living_area",), ("property_type",),
            ("latitude",), ("longitude",), ("img_src",),
            ("detail_url",), ("days_on_zillow",), ("listing_status",)
        ]
        mock_conn.cursor.return_value = mock_cursor
        mock_db_conn.return_value.__enter__.return_value = mock_conn

        response = client.get("/api/properties/search?property_type=forsale")
        data = response.get_json()

        assert response.status_code == 200
        assert len(data["properties"]) == 1
        assert data["properties"][0]["pricePerSqft"] == 200.0

    @patch("bna_market.web.api.routes.get_app_db_connection")
    def test_search_handles_zero_living_area(self, mock_db_conn, client):
        """Should handle properties with zero living area gracefully"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (1,)
        mock_cursor.fetchall.return_value = [
            (123, "123 Main St", 300000, 3, 2, 0, "SINGLE_FAMILY",
             36.1, -86.8, "img.jpg", "/homedetails/123", 10, "FOR_SALE")
        ]
        mock_cursor.description = [
            ("zpid",), ("address",), ("price",), ("bedrooms",),
            ("bathrooms",), ("living_area",), ("property_type",),
            ("latitude",), ("longitude",), ("img_src",),
            ("detail_url",), ("days_on_zillow",), ("listing_status",)
        ]
        mock_conn.cursor.return_value = mock_cursor
        mock_db_conn.return_value.__enter__.return_value = mock_conn

        response = client.get("/api/properties/search?property_type=forsale")
        data = response.get_json()

        assert response.status_code == 200
        assert data["properties"][0]["pricePerSqft"] is None


class TestExportFiltersComprehensive:
    """Additional tests for export filter coverage"""

    @patch("bna_market.web.api.routes.get_app_db_connection")
    def test_export_applies_all_filters(self, mock_db_conn, client):
        """Should apply all filters to export"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_cursor.description = [
            ("zpid",), ("address",), ("price",), ("bedrooms",),
            ("bathrooms",), ("living_area",), ("property_type",),
            ("latitude",), ("longitude",), ("days_on_zillow",),
            ("listing_status",), ("detail_url",)
        ]
        mock_conn.cursor.return_value = mock_cursor
        mock_db_conn.return_value.__enter__.return_value = mock_conn

        response = client.get(
            "/api/properties/export?property_type=forsale"
            "&min_price=100000&max_price=500000"
            "&min_beds=2&max_beds=5"
            "&min_baths=1&max_baths=3"
            "&min_sqft=1000&max_sqft=3000"
            "&city=Nashville&zip_code=37201"
        )
        assert response.status_code == 200

        calls = mock_cursor.execute.call_args_list
        query = calls[0][0][0]
        assert "price >= %s" in query
        assert "price <= %s" in query
        assert "bedrooms >= %s" in query
        assert "bedrooms <= %s" in query
        assert "bathrooms >= %s" in query
        assert "bathrooms <= %s" in query
        assert "living_area >= %s" in query
        assert "living_area <= %s" in query
        assert "LOWER(address) LIKE %s" in query
        assert "address LIKE %s" in query


class TestFredMetricsFiltersComprehensive:
    """Additional tests for FRED metrics filter coverage"""

    @patch("bna_market.web.api.routes.get_app_db_connection")
    def test_fred_metrics_filters_by_series_id(self, mock_db_conn, client):
        """Should filter by series_id"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_cursor.description = [("date",), ("metric_name",), ("series_id",), ("value",)]
        mock_conn.cursor.return_value = mock_cursor
        mock_db_conn.return_value.__enter__.return_value = mock_conn

        response = client.get("/api/metrics/fred?series_id=NASHTNSA")
        assert response.status_code == 200

        calls = mock_cursor.execute.call_args_list
        query = calls[0][0][0]
        assert "series_id = %s" in query


class TestZillowUrlFixer:
    """Tests for fix_zillow_url function"""

    def test_fix_zillow_url_handles_none(self, client):
        """Should handle None URL gracefully"""
        from bna_market.web.api.routes import fix_zillow_url
        assert fix_zillow_url(None) is None

    def test_fix_zillow_url_handles_empty_string(self, client):
        """Should handle empty string URL"""
        from bna_market.web.api.routes import fix_zillow_url
        assert fix_zillow_url("") is None

    def test_fix_zillow_url_adds_domain_to_relative_path(self, client):
        """Should add Zillow domain to relative URLs"""
        from bna_market.web.api.routes import fix_zillow_url
        result = fix_zillow_url("/homedetails/123")
        assert result == "https://www.zillow.com/homedetails/123"

    def test_fix_zillow_url_preserves_absolute_url(self, client):
        """Should preserve absolute URLs"""
        from bna_market.web.api.routes import fix_zillow_url
        url = "https://www.zillow.com/homedetails/123"
        assert fix_zillow_url(url) == url


class TestErrorHandling:
    """Tests for error handling in routes"""

    @patch("bna_market.web.api.routes.get_app_db_connection")
    def test_search_handles_invalid_page_number(self, mock_db_conn, client):
        """Should handle invalid page numbers gracefully"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (10,)
        mock_cursor.fetchall.return_value = []
        mock_cursor.description = [
            ("zpid",), ("address",), ("price",), ("bedrooms",),
            ("bathrooms",), ("living_area",), ("property_type",),
            ("latitude",), ("longitude",), ("img_src",),
            ("detail_url",), ("days_on_zillow",), ("listing_status",)
        ]
        mock_conn.cursor.return_value = mock_cursor
        mock_db_conn.return_value.__enter__.return_value = mock_conn

        # Test negative page (should default to 1)
        response = client.get("/api/properties/search?property_type=forsale&page=-1")
        assert response.status_code == 200
        data = response.get_json()
        assert data["pagination"]["page"] == 1

    @patch("bna_market.web.api.routes.get_app_db_connection")
    def test_search_limits_per_page_to_100(self, mock_db_conn, client):
        """Should limit per_page to maximum of 100"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (200,)
        mock_cursor.fetchall.return_value = []
        mock_cursor.description = [
            ("zpid",), ("address",), ("price",), ("bedrooms",),
            ("bathrooms",), ("living_area",), ("property_type",),
            ("latitude",), ("longitude",), ("img_src",),
            ("detail_url",), ("days_on_zillow",), ("listing_status",)
        ]
        mock_conn.cursor.return_value = mock_cursor
        mock_db_conn.return_value.__enter__.return_value = mock_conn

        response = client.get("/api/properties/search?property_type=forsale&per_page=500")
        assert response.status_code == 200
        data = response.get_json()
        assert data["pagination"]["perPage"] == 100
