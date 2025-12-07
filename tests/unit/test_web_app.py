"""
Unit tests for Flask web application with Supabase mocking
"""

import pytest
from unittest.mock import patch, MagicMock
from contextlib import contextmanager

from bna_market.web.app import create_app


class MockCursor:
    """Mock database cursor for testing"""

    def __init__(self, data=None, columns=None):
        self._data = data or []
        self._columns = columns or []

    def execute(self, query, params=None):
        pass

    def fetchone(self):
        return self._data[0] if self._data else None

    def fetchall(self):
        return self._data

    @property
    def description(self):
        return [(col,) for col in self._columns]


class MockConnection:
    """Mock database connection for testing"""

    def __init__(self, cursor):
        self._cursor = cursor

    def cursor(self):
        return self._cursor

    def commit(self):
        pass

    def rollback(self):
        pass

    def close(self):
        pass


@pytest.fixture
def mock_db_with_data():
    """Mock database with sample data"""
    # Sample data for properties
    forsale_data = [
        (1, "123 Main St, Nashville, TN", 350000, 3, 2.0, 1800,
         "SINGLE_FAMILY", 36.16, -86.78, None, "/homedetails/1", 5, "FOR_SALE"),
        (2, "456 Oak Ave, Nashville, TN", 420000, 4, 3.0, 2200,
         "SINGLE_FAMILY", 36.15, -86.80, None, "/homedetails/2", 10, "FOR_SALE"),
    ]

    rentals_data = [
        (3, "789 Pine Dr, Nashville, TN", 1800, 2, 1.0, 1000,
         "APARTMENT", 36.17, -86.79, None, "/homedetails/3", 7, "FOR_RENT"),
        (4, "321 Elm St, Nashville, TN", 2200, 3, 2.0, 1400,
         "TOWNHOUSE", 36.14, -86.81, None, "/homedetails/4", 3, "FOR_RENT"),
    ]

    fred_data = [
        ("2024-03-01", "median_price", "SERIES1", 302000),
        ("2024-02-22", "median_price", "SERIES1", 301000),
        ("2024-03-01", "active_listings", "SERIES2", 1540),
        ("2024-03-01", "median_dom", "SERIES3", 34),
    ]

    property_columns = [
        "zpid", "address", "price", "bedrooms", "bathrooms", "livingArea",
        "propertyType", "latitude", "longitude", "imgSrc", "detailUrl",
        "daysOnZillow", "listingStatus"
    ]

    fred_columns = ["date", "metricName", "seriesId", "value"]

    class SmartMockCursor:
        def __init__(self):
            self._data = []
            self._description = []

        def execute(self, query, params=None):
            query_lower = query.lower()
            if "count(*)" in query_lower and "avg" in query_lower:
                if "bna_rentals" in query_lower:
                    self._data = [(2, 2000)]
                else:
                    self._data = [(2, 385000)]
                self._description = [("count",), ("avg_price",)]
            elif "bna_rentals" in query_lower:
                self._data = rentals_data
                self._description = [(col,) for col in property_columns]
            elif "bna_forsale" in query_lower:
                self._data = forsale_data
                self._description = [(col,) for col in property_columns]
            elif "bna_fred_metrics" in query_lower:
                self._data = fred_data
                self._description = [(col,) for col in fred_columns]
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
    def mock_get_db():
        yield SmartMockConnection()

    return mock_get_db


@pytest.fixture
def mock_empty_db():
    """Mock empty database"""

    class EmptyCursor:
        def __init__(self):
            self._data = []
            self._description = []

        def execute(self, query, params=None):
            query_lower = query.lower()
            if "count(*)" in query_lower:
                self._data = [(0, None)]
                self._description = [("count",), ("avg_price",)]
            else:
                self._data = []
                self._description = []

        def fetchone(self):
            return self._data[0] if self._data else (0, None)

        def fetchall(self):
            return self._data

        @property
        def description(self):
            return self._description

    class EmptyConnection:
        def cursor(self):
            return EmptyCursor()

        def commit(self):
            pass

        def rollback(self):
            pass

        def close(self):
            pass

    @contextmanager
    def mock_get_db():
        yield EmptyConnection()

    return mock_get_db


class TestCreateApp:
    """Tests for Flask app factory"""

    def test_create_app_without_config(self):
        """Should create Flask app with default config"""
        app = create_app()
        assert app is not None

    def test_create_app_with_custom_config(self):
        """Should override config with custom values"""
        custom_config = {"TESTING": True, "CUSTOM_KEY": "test_value"}
        app = create_app(config=custom_config)

        assert app.config["TESTING"] is True
        assert app.config["CUSTOM_KEY"] == "test_value"

    def test_app_registers_api_blueprint(self):
        """Should register API blueprint"""
        app = create_app()
        assert "api" in [bp.name for bp in app.blueprints.values()]

    def test_app_has_api_dashboard_route(self):
        """Should have API dashboard route registered"""
        app = create_app()
        rules = [str(rule) for rule in app.url_map.iter_rules()]
        assert "/api/dashboard" in rules


class TestAPIDashboardRoute:
    """Tests for API dashboard endpoint (Vue frontend consumes this)"""

    def test_api_dashboard_with_data(self, mock_db_with_data):
        """Should return dashboard JSON with property and FRED data"""
        app = create_app(config={"TESTING": True})

        with patch("bna_market.web.api.routes.get_db_connection", mock_db_with_data):
            client = app.test_client()
            response = client.get("/api/dashboard")

            assert response.status_code == 200
            data = response.get_json()
            assert "propertyKPIs" in data
            assert "fredKPIs" in data
            assert "rentals" in data
            assert "forsale" in data

    def test_api_dashboard_with_empty_database(self, mock_empty_db):
        """Should return dashboard JSON with zero counts for empty database"""
        app = create_app(config={"TESTING": True})

        with patch("bna_market.web.api.routes.get_db_connection", mock_empty_db):
            client = app.test_client()
            response = client.get("/api/dashboard")

            assert response.status_code == 200
            data = response.get_json()
            assert data["propertyKPIs"]["totalRentalListings"] == 0
            assert data["propertyKPIs"]["totalForSaleListings"] == 0

    def test_api_dashboard_calculates_property_kpis(self, mock_db_with_data):
        """Should calculate property KPIs correctly"""
        app = create_app(config={"TESTING": True})

        with patch("bna_market.web.api.routes.get_db_connection", mock_db_with_data):
            client = app.test_client()
            response = client.get("/api/dashboard")

            assert response.status_code == 200
            data = response.get_json()
            # Verify KPIs are calculated (2 forsale, 2 rental in mock data)
            assert data["propertyKPIs"]["totalForSaleListings"] == 2
            assert data["propertyKPIs"]["totalRentalListings"] == 2
            assert data["propertyKPIs"]["avgSalePrice"] is not None

    def test_api_dashboard_handles_db_error_gracefully(self):
        """Should return error for database connection failure"""
        app = create_app(config={"TESTING": True})

        @contextmanager
        def failing_db():
            raise Exception("Database connection failed")
            yield  # Never reached

        with patch("bna_market.web.api.routes.get_db_connection", failing_db):
            client = app.test_client()
            response = client.get("/api/dashboard")

            assert response.status_code == 500
            data = response.get_json()
            assert "error" in data

    def test_api_dashboard_returns_fred_metrics(self, mock_db_with_data):
        """Should return FRED metrics when available"""
        app = create_app(config={"TESTING": True})

        with patch("bna_market.web.api.routes.get_db_connection", mock_db_with_data):
            client = app.test_client()
            response = client.get("/api/dashboard")
            data = response.get_json()

            assert response.status_code == 200
            assert "fredMetrics" in data
            assert len(data["fredMetrics"]) > 0

    def test_api_dashboard_returns_properties(self, mock_db_with_data):
        """Should return property arrays for rentals and forsale"""
        app = create_app(config={"TESTING": True})

        with patch("bna_market.web.api.routes.get_db_connection", mock_db_with_data):
            client = app.test_client()
            response = client.get("/api/dashboard")
            data = response.get_json()

            assert response.status_code == 200
            assert isinstance(data["rentals"], list)
            assert isinstance(data["forsale"], list)


class TestAppIntegration:
    """Integration tests for Flask app"""

    def test_app_serves_static_files(self):
        """Should be configured to serve static files"""
        app = create_app()
        assert app.static_folder is not None

    def test_app_has_template_folder(self):
        """Should be configured with template folder"""
        app = create_app()
        assert app.template_folder is not None

    def test_app_context_available(self):
        """Should have working application context"""
        app = create_app()
        with app.app_context():
            assert app.config is not None
