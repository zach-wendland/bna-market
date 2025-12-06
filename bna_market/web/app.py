"""
Flask application factory for BNA Market dashboard
"""

import math
import sqlite3
import os
from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from flask import Flask, render_template

from bna_market.utils.logger import setup_logger
from bna_market.core.config import settings, DATABASE_CONFIG

logger = setup_logger("web_app")


def get_last_updated(db_path: str) -> str | None:
    """
    Get the last updated timestamp from database file modification time

    Args:
        db_path: Path to the SQLite database

    Returns:
        Formatted timestamp string or None if unavailable
    """
    try:
        if os.path.exists(db_path):
            mtime = os.path.getmtime(db_path)
            dt = datetime.fromtimestamp(mtime)
            return dt.strftime("%B %d, %Y at %I:%M %p")
    except Exception:
        pass
    return None


def get_relative_time(db_path: str) -> str | None:
    """
    Get relative time since last update (e.g., '2 hours ago')

    Args:
        db_path: Path to the SQLite database

    Returns:
        Relative time string or None if unavailable
    """
    try:
        if os.path.exists(db_path):
            mtime = os.path.getmtime(db_path)
            dt = datetime.fromtimestamp(mtime)
            delta = datetime.now() - dt
            hours = delta.total_seconds() / 3600

            if hours < 1:
                minutes = int(delta.total_seconds() / 60)
                return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
            elif hours < 24:
                hours_int = int(hours)
                return f"{hours_int} hour{'s' if hours_int != 1 else ''} ago"
            else:
                days = int(hours / 24)
                return f"{days} day{'s' if days != 1 else ''} ago"
    except Exception:
        pass
    return None


def create_app(config=None):
    """
    Application factory for Flask app

    Args:
        config: Optional configuration dict

    Returns:
        Configured Flask application
    """
    # Determine paths relative to package root
    template_folder = os.path.join(os.path.dirname(__file__), "templates")
    static_folder = os.path.join(os.path.dirname(__file__), "static")

    app = Flask(
        __name__, template_folder=template_folder, static_folder=static_folder
    )

    # Default configuration from settings
    app.config["DATABASE_PATH"] = DATABASE_CONFIG["path"]

    # Override with custom config if provided
    if config:
        app.config.update(config)

    # Register blueprints
    from bna_market.web.api import api_bp
    app.register_blueprint(api_bp)

    # Helper function for reading DataFrames
    def read_df(table):
        con = sqlite3.connect(app.config["DATABASE_PATH"])
        df = pd.read_sql_query(f"SELECT * FROM {table}", con)
        con.close()
        return df

    @app.route("/")
    def dashboard():
        db_path = app.config["DATABASE_PATH"]

        # Read property data with error handling
        # PERFORMANCE FIX: Convert to list of dicts instead of DataFrames
        # This avoids slow iterrows() in templates (18x faster)
        try:
            rentals_df = read_df("BNA_RENTALS")
            rentals = rentals_df.to_dict('records') if not rentals_df.empty else []
        except Exception as e:
            logger.warning(f"Could not read BNA_RENTALS table: {e}")
            rentals_df = pd.DataFrame()
            rentals = []

        try:
            forsale_df = read_df("BNA_FORSALE")
            forsale = forsale_df.to_dict('records') if not forsale_df.empty else []
        except Exception as e:
            logger.warning(f"Could not read BNA_FORSALE table: {e}")
            forsale_df = pd.DataFrame()
            forsale = []

        # Read FRED metrics data
        try:
            fred_metrics = read_df("BNA_FRED_METRICS")
            fred_metrics["date"] = pd.to_datetime(fred_metrics["date"])
        except Exception as e:
            fred_metrics = pd.DataFrame()

        # Property KPIs - using list comprehension for performance
        # Filter out None and NaN values
        rental_prices = [
            r.get('price') for r in rentals
            if r.get('price') is not None and not (isinstance(r.get('price'), float) and math.isnan(r.get('price')))
        ]
        forsale_prices = [
            f.get('price') for f in forsale
            if f.get('price') is not None and not (isinstance(f.get('price'), float) and math.isnan(f.get('price')))
        ]

        property_kpis = {
            "Total Rental Listings": len(rentals),
            "Avg Rental Price": (
                f"${round(sum(rental_prices) / len(rental_prices)):,}"
                if rental_prices else "N/A"
            ),
            "Total For-Sale Listings": len(forsale),
            "Avg Sale Price": (
                f"${round(sum(forsale_prices) / len(forsale_prices)):,}"
                if forsale_prices else "N/A"
            ),
        }

        # FRED Economic KPIs (latest values)
        fred_kpis = {}
        if not fred_metrics.empty:
            latest_metrics = fred_metrics.sort_values("date").groupby("metric_name").last()

            metric_display_names = {
                "median_price": "Median Listing Price",
                "active_listings": "Active Listings",
                "median_dom": "Median Days on Market",
                "employment_non_farm": "Non-Farm Employment",
                "msa_population": "MSA Population",
                "msa_per_capita_income": "Per Capita Income",
            }

            for metric_name, display_name in metric_display_names.items():
                if metric_name in latest_metrics.index:
                    value = latest_metrics.loc[metric_name, "value"]
                    if metric_name == "median_price":
                        fred_kpis[display_name] = f"${int(value):,}"
                    elif metric_name in ["active_listings", "median_dom"]:
                        fred_kpis[display_name] = f"{int(value):,}"
                    elif metric_name == "employment_non_farm":
                        fred_kpis[display_name] = f"{int(value/1000)}K"
                    elif metric_name == "msa_population":
                        fred_kpis[display_name] = f"{int(value)}K"
                    elif metric_name == "msa_per_capita_income":
                        fred_kpis[display_name] = f"${int(value):,}"

        # Rental price histogram
        if not rentals_df.empty and "price" in rentals_df.columns:
            fig_rent_hist = px.histogram(
                rentals_df,
                x="price",
                title="Rental Price Distribution",
                labels={"price": "Monthly Rent ($)", "count": "Number of Listings"},
                color_discrete_sequence=["#1f77b4"],
            )
            fig_rent_hist.update_layout(
                template="plotly_white",
                font=dict(family="Arial, sans-serif", size=12),
                title_font_size=16,
                showlegend=False,
            )
        else:
            fig_rent_hist = go.Figure()
            fig_rent_hist.add_annotation(
                text="No rental data available. Please run 'python -m bna_market etl' to populate the database.",
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                showarrow=False,
                font=dict(size=14, color="gray"),
            )
            fig_rent_hist.update_layout(title="Rental Price Distribution", template="plotly_white")

        # For-sale price histogram
        if not forsale_df.empty and "price" in forsale_df.columns:
            fig_sale_hist = px.histogram(
                forsale_df,
                x="price",
                title="For-Sale Price Distribution",
                labels={"price": "Sale Price ($)", "count": "Number of Listings"},
                color_discrete_sequence=["#2ca02c"],
            )
            fig_sale_hist.update_layout(
                template="plotly_white",
                font=dict(family="Arial, sans-serif", size=12),
                title_font_size=16,
                showlegend=False,
            )
        else:
            fig_sale_hist = go.Figure()
            fig_sale_hist.add_annotation(
                text="No for-sale data available. Please run 'python -m bna_market etl' to populate the database.",
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                showarrow=False,
                font=dict(size=14, color="gray"),
            )
            fig_sale_hist.update_layout(title="For-Sale Price Distribution", template="plotly_white")

        # FRED metrics time series charts
        fred_charts = {}
        if not fred_metrics.empty:
            # Median price trend
            median_price_data = (
                fred_metrics[fred_metrics["metric_name"] == "median_price"]
                .sort_values("date")
            )
            if not median_price_data.empty:
                fig_median_price = px.line(
                    median_price_data,
                    x="date",
                    y="value",
                    title="Median Listing Price Over Time",
                    labels={"date": "Date", "value": "Price ($)"},
                )
                fig_median_price.update_traces(line_color="#ff7f0e", line_width=2)
                fig_median_price.update_layout(
                    template="plotly_white",
                    font=dict(family="Arial, sans-serif", size=12),
                    title_font_size=16,
                    hovermode="x unified",
                )
                fred_charts["median_price"] = pio.to_html(
                    fig_median_price, full_html=False, include_plotlyjs=False
                )

            # Active listings trend
            active_listings_data = (
                fred_metrics[fred_metrics["metric_name"] == "active_listings"]
                .sort_values("date")
            )
            if not active_listings_data.empty:
                fig_active = px.line(
                    active_listings_data,
                    x="date",
                    y="value",
                    title="Active Listings Over Time",
                    labels={"date": "Date", "value": "Number of Listings"},
                )
                fig_active.update_traces(line_color="#d62728", line_width=2)
                fig_active.update_layout(
                    template="plotly_white",
                    font=dict(family="Arial, sans-serif", size=12),
                    title_font_size=16,
                    hovermode="x unified",
                )
                fred_charts["active_listings"] = pio.to_html(
                    fig_active, full_html=False, include_plotlyjs=False
                )

            # Employment trend
            employment_data = (
                fred_metrics[fred_metrics["metric_name"] == "employment_non_farm"]
                .sort_values("date")
            )
            if not employment_data.empty:
                fig_employment = px.line(
                    employment_data,
                    x="date",
                    y="value",
                    title="Non-Farm Employment Over Time",
                    labels={"date": "Date", "value": "Employment (thousands)"},
                )
                fig_employment.update_traces(line_color="#9467bd", line_width=2)
                fig_employment.update_layout(
                    template="plotly_white",
                    font=dict(family="Arial, sans-serif", size=12),
                    title_font_size=16,
                    hovermode="x unified",
                )
                fred_charts["employment"] = pio.to_html(
                    fig_employment, full_html=False, include_plotlyjs=False
                )

            # Days on market trend
            dom_data = (
                fred_metrics[fred_metrics["metric_name"] == "median_dom"]
                .sort_values("date")
            )
            if not dom_data.empty:
                fig_dom = px.line(
                    dom_data,
                    x="date",
                    y="value",
                    title="Median Days on Market Over Time",
                    labels={"date": "Date", "value": "Days"},
                )
                fig_dom.update_traces(line_color="#8c564b", line_width=2)
                fig_dom.update_layout(
                    template="plotly_white",
                    font=dict(family="Arial, sans-serif", size=12),
                    title_font_size=16,
                    hovermode="x unified",
                )
                fred_charts["dom"] = pio.to_html(
                    fig_dom, full_html=False, include_plotlyjs=False
                )

        plots = {
            "rent_price_hist": pio.to_html(
                fig_rent_hist, full_html=False, include_plotlyjs="cdn"
            ),
            "sale_price_hist": pio.to_html(
                fig_sale_hist, full_html=False, include_plotlyjs=False
            ),
        }

        # Get data freshness information
        last_updated = get_last_updated(db_path)
        relative_time = get_relative_time(db_path)

        return render_template(
            "dashboard.html",
            property_kpis=property_kpis,
            fred_kpis=fred_kpis,
            plots=plots,
            fred_charts=fred_charts,
            rentals=rentals,
            forsale=forsale,
            last_updated=last_updated,
            relative_time=relative_time,
        )

    return app


# For backwards compatibility when running directly
if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=5000)
