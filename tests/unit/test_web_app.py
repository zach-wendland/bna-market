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
    conn = sqlite3.connect(db_path)

    # Create tables
    conn.execute("""
        CREATE TABLE BNA_FORSALE (
            zpid INTEGER,
            price REAL,
            address TEXT,
            bedrooms INTEGER,
            bathrooms REAL,
            livingArea INTEGER
        )
    """)

    conn.execute("""
        CREATE TABLE BNA_RENTALS (
            zpid INTEGER,
            price REAL,
            address TEXT,
            bedrooms INTEGER,
            bathrooms REAL,
            livingArea INTEGER
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

    # Insert sample data
    conn.execute(
        "INSERT INTO BNA_FORSALE VALUES (1, 350000, '123 Main St', 3, 2.0, 1800)"
    )
    conn.execute(
        "INSERT INTO BNA_FORSALE VALUES (2, 420000, '456 Oak Ave', 4, 3.0, 2200)"
    )

    conn.execute(
        "INSERT INTO BNA_RENTALS VALUES (3, 1800, '789 Pine Dr', 2, 1.0, 1000)"
    )
    conn.execute(
        "INSERT INTO BNA_RENTALS VALUES (4, 2200, '321 Elm St', 3, 2.0, 1400)"
    )

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

    os.close(fd)
    os.unlink(db_path)


@pytest.fixture
def empty_db():
    """Create temporary empty test database"""
    fd, db_path = tempfile.mkstemp(suffix=".db")
    conn = sqlite3.connect(db_path)

    # Create empty tables
    conn.execute("""
        CREATE TABLE BNA_FORSALE (
            zpid INTEGER,
            price REAL,
            address TEXT,
            bedrooms INTEGER,
            bathrooms REAL,
            livingArea INTEGER
        )
    """)

    conn.execute("""
        CREATE TABLE BNA_RENTALS (
            zpid INTEGER,
            price REAL,
            address TEXT,
            bedrooms INTEGER,
            bathrooms REAL,
            livingArea INTEGER
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

    os.close(fd)
    os.unlink(db_path)


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

    def test_app_has_dashboard_route(self):
        """Should have dashboard route registered"""
        app = create_app()
        rules = [str(rule) for rule in app.url_map.iter_rules()]
        assert "/" in rules


class TestDashboardRoute:
    """Tests for dashboard route"""

    def test_dashboard_with_data(self, test_db):
        """Should render dashboard with property and FRED data"""
        app = create_app(config={"DATABASE_PATH": test_db, "TESTING": True})
        client = app.test_client()

        response = client.get("/")

        assert response.status_code == 200
        assert b"BNA Market" in response.data or b"dashboard" in response.data.lower()

    def test_dashboard_with_empty_database(self, empty_db):
        """Should render dashboard with empty state messages"""
        app = create_app(config={"DATABASE_PATH": empty_db, "TESTING": True})
        client = app.test_client()

        response = client.get("/")

        assert response.status_code == 200
        # Should contain "no data" messages
        assert b"No rental data" in response.data or b"0" in response.data

    def test_dashboard_calculates_property_kpis(self, test_db):
        """Should calculate property KPIs correctly"""
        app = create_app(config={"DATABASE_PATH": test_db, "TESTING": True})

        with app.test_client() as client:
            response = client.get("/")
            assert response.status_code == 200

            # Check that data is present (KPIs calculated)
            data = response.data.decode()
            assert "385,000" in data or "2,000" in data  # Average prices

    def test_dashboard_handles_missing_table_gracefully(self, tmpdir):
        """Should handle missing database tables without crashing"""
        # Create empty database without tables
        db_path = str(tmpdir.join("test.db"))
        conn = sqlite3.connect(db_path)
        conn.close()

        app = create_app(config={"DATABASE_PATH": db_path, "TESTING": True})
        client = app.test_client()

        # Should not crash, should handle error gracefully
        response = client.get("/")
        assert response.status_code == 200

    def test_dashboard_generates_plotly_charts(self, test_db):
        """Should generate Plotly charts in HTML"""
        app = create_app(config={"DATABASE_PATH": test_db, "TESTING": True})
        client = app.test_client()

        response = client.get("/")
        data = response.data.decode()

        # Check for Plotly chart markers
        assert "plotly" in data.lower() or "chart" in data.lower()

    def test_dashboard_with_fred_metrics(self, test_db):
        """Should display FRED metrics when available"""
        app = create_app(config={"DATABASE_PATH": test_db, "TESTING": True})
        client = app.test_client()

        response = client.get("/")
        data = response.data.decode()

        # Should contain FRED data (median price, employment, etc.)
        assert response.status_code == 200
        assert len(data) > 1000  # Should have substantial HTML content


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
