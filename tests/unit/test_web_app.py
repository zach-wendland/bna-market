"""
Unit tests for Flask web application
"""

import pytest
import sqlite3
import tempfile
import os
import pandas as pd
from datetime import datetime, timedelta

from bna_market.web.app import create_app


@pytest.fixture
def test_db():
    """Create temporary test database with sample data"""
    fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)  # Close file descriptor immediately on Windows
    conn = sqlite3.connect(db_path)

    # Create tables with full schema to match dashboard queries
    conn.execute("""
        CREATE TABLE BNA_FORSALE (
            zpid INTEGER,
            price REAL,
            address TEXT,
            bedrooms INTEGER,
            bathrooms REAL,
            livingArea INTEGER,
            propertyType TEXT,
            latitude REAL,
            longitude REAL,
            imgSrc TEXT,
            detailUrl TEXT,
            daysOnZillow INTEGER,
            listingStatus TEXT
        )
    """)

    conn.execute("""
        CREATE TABLE BNA_RENTALS (
            zpid INTEGER,
            price REAL,
            address TEXT,
            bedrooms INTEGER,
            bathrooms REAL,
            livingArea INTEGER,
            propertyType TEXT,
            latitude REAL,
            longitude REAL,
            imgSrc TEXT,
            detailUrl TEXT,
            daysOnZillow INTEGER,
            listingStatus TEXT
        )
    """)

    conn.execute("""
        CREATE TABLE BNA_FRED_METRICS (
            date TEXT,
            metric_name TEXT,
            series_id TEXT,
            value REAL
        )
    """)

    # Insert sample data with full columns
    conn.execute("""
        INSERT INTO BNA_FORSALE VALUES
        (1, 350000, '123 Main St, Nashville, TN', 3, 2.0, 1800, 'SINGLE_FAMILY', 36.16, -86.78, NULL, '/homedetails/1', 5, 'FOR_SALE')
    """)
    conn.execute("""
        INSERT INTO BNA_FORSALE VALUES
        (2, 420000, '456 Oak Ave, Nashville, TN', 4, 3.0, 2200, 'SINGLE_FAMILY', 36.15, -86.80, NULL, '/homedetails/2', 10, 'FOR_SALE')
    """)

    conn.execute("""
        INSERT INTO BNA_RENTALS VALUES
        (3, 1800, '789 Pine Dr, Nashville, TN', 2, 1.0, 1000, 'APARTMENT', 36.17, -86.79, NULL, '/homedetails/3', 7, 'FOR_RENT')
    """)
    conn.execute("""
        INSERT INTO BNA_RENTALS VALUES
        (4, 2200, '321 Elm St, Nashville, TN', 3, 2.0, 1400, 'TOWNHOUSE', 36.14, -86.81, NULL, '/homedetails/4', 3, 'FOR_RENT')
    """)

    # Insert FRED metrics with recent dates
    base_date = datetime.now() - timedelta(days=30)
    for i in range(5):
        date = (base_date + timedelta(days=i*7)).strftime("%Y-%m-%d")
        conn.execute(
            f"INSERT INTO BNA_FRED_METRICS VALUES ('{date}', 'median_price', 'SERIES1', {300000 + i*1000})"
        )
        conn.execute(
            f"INSERT INTO BNA_FRED_METRICS VALUES ('{date}', 'active_listings', 'SERIES2', {1500 + i*10})"
        )
        conn.execute(
            f"INSERT INTO BNA_FRED_METRICS VALUES ('{date}', 'median_dom', 'SERIES3', {30 + i})"
        )
        conn.execute(
            f"INSERT INTO BNA_FRED_METRICS VALUES ('{date}', 'employment_non_farm', 'SERIES4', {950000 + i*100})"
        )

    conn.commit()
    conn.close()

    yield db_path

    # Cleanup - file descriptor already closed at the start
    try:
        os.unlink(db_path)
    except PermissionError:
        pass  # On Windows, file might still be locked


@pytest.fixture
def empty_db():
    """Create temporary empty test database"""
    fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)  # Close file descriptor immediately on Windows
    conn = sqlite3.connect(db_path)

    # Create empty tables with full schema
    conn.execute("""
        CREATE TABLE BNA_FORSALE (
            zpid INTEGER,
            price REAL,
            address TEXT,
            bedrooms INTEGER,
            bathrooms REAL,
            livingArea INTEGER,
            propertyType TEXT,
            latitude REAL,
            longitude REAL,
            imgSrc TEXT,
            detailUrl TEXT,
            daysOnZillow INTEGER,
            listingStatus TEXT
        )
    """)

    conn.execute("""
        CREATE TABLE BNA_RENTALS (
            zpid INTEGER,
            price REAL,
            address TEXT,
            bedrooms INTEGER,
            bathrooms REAL,
            livingArea INTEGER,
            propertyType TEXT,
            latitude REAL,
            longitude REAL,
            imgSrc TEXT,
            detailUrl TEXT,
            daysOnZillow INTEGER,
            listingStatus TEXT
        )
    """)

    conn.execute("""
        CREATE TABLE BNA_FRED_METRICS (
            date TEXT,
            metric_name TEXT,
            series_id TEXT,
            value REAL
        )
    """)

    conn.commit()
    conn.close()

    yield db_path

    # Cleanup - file descriptor already closed above
    try:
        os.unlink(db_path)
    except PermissionError:
        pass  # On Windows, file might still be locked


class TestCreateApp:
    """Tests for Flask app factory"""

    def test_create_app_without_config(self):
        """Should create Flask app with default config"""
        app = create_app()
        assert app is not None
        assert "DATABASE_PATH" in app.config

    def test_create_app_with_custom_config(self, test_db):
        """Should override config with custom values"""
        custom_config = {"DATABASE_PATH": test_db, "TESTING": True}
        app = create_app(config=custom_config)

        assert app.config["DATABASE_PATH"] == test_db
        assert app.config["TESTING"] is True

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

    def test_api_dashboard_with_data(self, test_db):
        """Should return dashboard JSON with property and FRED data"""
        app = create_app(config={"DATABASE_PATH": test_db, "TESTING": True})
        client = app.test_client()

        response = client.get("/api/dashboard")

        assert response.status_code == 200
        data = response.get_json()
        assert "propertyKPIs" in data
        assert "fredKPIs" in data
        assert "rentals" in data
        assert "forsale" in data

    def test_api_dashboard_with_empty_database(self, empty_db):
        """Should return dashboard JSON with zero counts for empty database"""
        app = create_app(config={"DATABASE_PATH": empty_db, "TESTING": True})
        client = app.test_client()

        response = client.get("/api/dashboard")

        assert response.status_code == 200
        data = response.get_json()
        assert data["propertyKPIs"]["totalRentalListings"] == 0
        assert data["propertyKPIs"]["totalForSaleListings"] == 0

    def test_api_dashboard_calculates_property_kpis(self, test_db):
        """Should calculate property KPIs correctly"""
        app = create_app(config={"DATABASE_PATH": test_db, "TESTING": True})

        with app.test_client() as client:
            response = client.get("/api/dashboard")
            assert response.status_code == 200

            data = response.get_json()
            # Verify KPIs are calculated (2 forsale, 2 rental in test_db)
            assert data["propertyKPIs"]["totalForSaleListings"] == 2
            assert data["propertyKPIs"]["totalRentalListings"] == 2
            assert data["propertyKPIs"]["avgSalePrice"] is not None

    def test_api_dashboard_handles_missing_table_gracefully(self, tmpdir):
        """Should return error for missing database tables"""
        # Create empty database without tables
        db_path = str(tmpdir.join("test.db"))
        conn = sqlite3.connect(db_path)
        conn.close()

        app = create_app(config={"DATABASE_PATH": db_path, "TESTING": True})
        client = app.test_client()

        # Should return 500 with error message (tables don't exist)
        response = client.get("/api/dashboard")
        assert response.status_code == 500
        data = response.get_json()
        assert "error" in data

    def test_api_dashboard_returns_fred_metrics(self, test_db):
        """Should return FRED metrics when available"""
        app = create_app(config={"DATABASE_PATH": test_db, "TESTING": True})
        client = app.test_client()

        response = client.get("/api/dashboard")
        data = response.get_json()

        assert response.status_code == 200
        assert "fredMetrics" in data
        assert len(data["fredMetrics"]) > 0

    def test_api_dashboard_returns_properties(self, test_db):
        """Should return property arrays for rentals and forsale"""
        app = create_app(config={"DATABASE_PATH": test_db, "TESTING": True})
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
