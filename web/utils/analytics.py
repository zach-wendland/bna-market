"""
Market analytics utilities for BNA Market application

Provides functions for statistical analysis and visualization of FRED metrics
and property data including correlation analysis, scatter plots with trendlines,
and comprehensive market indicator dashboards.

Required packages:
- pandas
- plotly
- scipy
- statsmodels (required for OLS trendlines in scatter plots)
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats
from typing import Dict, Optional, Tuple

# Check for statsmodels availability (required for trendline='ols')
try:
    import statsmodels.api as sm

    HAS_STATSMODELS = True
except ImportError:
    HAS_STATSMODELS = False


def calculate_correlations(fred_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate correlation matrix between FRED metrics

    Pivots the long-format FRED data to wide format and computes
    pairwise Pearson correlations between all metrics.

    Args:
        fred_df: Long-format DataFrame with columns: date, metric_name, series_id, value

    Returns:
        Correlation matrix DataFrame with metrics as both rows and columns
        Returns empty DataFrame if input is empty or has insufficient data
    """
    if fred_df.empty:
        return pd.DataFrame()

    # Ensure date column is datetime
    if "date" in fred_df.columns:
        fred_df = fred_df.copy()
        fred_df["date"] = pd.to_datetime(fred_df["date"])

    # Pivot from long to wide format
    wide_df = fred_df.pivot_table(
        index="date", columns="metric_name", values="value", aggfunc="first"
    )

    # Calculate correlation matrix
    if wide_df.empty or len(wide_df.columns) < 2:
        return pd.DataFrame()

    corr_matrix = wide_df.corr()

    return corr_matrix


def create_correlation_heatmap(corr_matrix: pd.DataFrame) -> str:
    """
    Create interactive correlation heatmap using Plotly

    Args:
        corr_matrix: Correlation matrix DataFrame

    Returns:
        HTML string of the heatmap figure
        Returns empty div with message if correlation matrix is empty
    """
    if corr_matrix.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="Insufficient data to calculate correlations",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=14, color="gray"),
        )
        fig.update_layout(
            title="FRED Metrics Correlation Heatmap", template="plotly_white", height=500
        )
        return fig.to_html(full_html=False, include_plotlyjs=False)

    # Create heatmap with Plotly Express
    fig = px.imshow(
        corr_matrix,
        text_auto=".2f",
        color_continuous_scale="RdBu_r",
        zmin=-1,
        zmax=1,
        aspect="auto",
        title="FRED Metrics Correlation Heatmap",
        labels=dict(color="Correlation"),
    )

    fig.update_layout(
        template="plotly_white",
        font=dict(family="Arial, sans-serif", size=12),
        title_font_size=16,
        height=500,
        xaxis_title="",
        yaxis_title="",
    )

    # Improve readability of axis labels
    fig.update_xaxes(tickangle=-45)

    return fig.to_html(full_html=False, include_plotlyjs=False)


def create_scatter_with_trendline(
    df: pd.DataFrame, x_metric: str, y_metric: str
) -> Tuple[str, Optional[float], Optional[float]]:
    """
    Create scatter plot with OLS trendline and correlation coefficient

    Args:
        df: Long-format DataFrame with columns: date, metric_name, value
        x_metric: Name of metric for x-axis
        y_metric: Name of metric for y-axis

    Returns:
        Tuple of (HTML string, correlation coefficient, p-value)
        Returns empty plot with message if insufficient data
    """
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No data available for scatter plot",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=14, color="gray"),
        )
        fig.update_layout(title=f"{y_metric} vs {x_metric}", template="plotly_white", height=400)
        return fig.to_html(full_html=False, include_plotlyjs=False), None, None

    # Pivot data to get both metrics on same row
    df_copy = df.copy()
    df_copy["date"] = pd.to_datetime(df_copy["date"])

    wide_df = df_copy.pivot_table(
        index="date", columns="metric_name", values="value", aggfunc="first"
    )

    # Check if both metrics exist
    if x_metric not in wide_df.columns or y_metric not in wide_df.columns:
        fig = go.Figure()
        fig.add_annotation(
            text=f"Metrics '{x_metric}' or '{y_metric}' not found in data",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=14, color="gray"),
        )
        fig.update_layout(title=f"{y_metric} vs {x_metric}", template="plotly_white", height=400)
        return fig.to_html(full_html=False, include_plotlyjs=False), None, None

    # Drop rows with missing values for either metric
    plot_df = wide_df[[x_metric, y_metric]].dropna()

    if len(plot_df) < 3:
        fig = go.Figure()
        fig.add_annotation(
            text="Insufficient data points for correlation analysis (need at least 3)",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=14, color="gray"),
        )
        fig.update_layout(title=f"{y_metric} vs {x_metric}", template="plotly_white", height=400)
        return fig.to_html(full_html=False, include_plotlyjs=False), None, None

    # Calculate Pearson correlation
    correlation, p_value = stats.pearsonr(plot_df[x_metric], plot_df[y_metric])

    # Create scatter plot with trendline (if statsmodels is available)
    if HAS_STATSMODELS:
        fig = px.scatter(
            plot_df,
            x=x_metric,
            y=y_metric,
            trendline="ols",
            title=f"{y_metric} vs {x_metric}<br><sub>Correlation: {correlation:.3f} (p={p_value:.4f})</sub>",
            labels={
                x_metric: x_metric.replace("_", " ").title(),
                y_metric: y_metric.replace("_", " ").title(),
            },
        )
    else:
        # Create scatter plot without trendline if statsmodels not available
        fig = px.scatter(
            plot_df,
            x=x_metric,
            y=y_metric,
            title=f"{y_metric} vs {x_metric}<br><sub>Correlation: {correlation:.3f} (p={p_value:.4f})</sub>",
            labels={
                x_metric: x_metric.replace("_", " ").title(),
                y_metric: y_metric.replace("_", " ").title(),
            },
        )

    fig.update_traces(
        marker=dict(size=8, opacity=0.6, color="#1f77b4"), selector=dict(mode="markers")
    )

    # Style the trendline (only if statsmodels is available and trendline was added)
    if HAS_STATSMODELS:
        fig.update_traces(line=dict(color="red", width=2, dash="dash"), selector=dict(mode="lines"))

    fig.update_layout(
        template="plotly_white",
        font=dict(family="Arial, sans-serif", size=12),
        title_font_size=16,
        height=400,
        hovermode="closest",
    )

    return fig.to_html(full_html=False, include_plotlyjs=False), correlation, p_value


def create_market_indicators_dashboard(
    fred_df: pd.DataFrame, properties_df: Optional[pd.DataFrame] = None
) -> Dict[str, str]:
    """
    Create comprehensive market indicators dashboard

    Generates multiple visualizations including correlation heatmap and
    key scatter plots showing relationships between market metrics.

    Args:
        fred_df: Long-format DataFrame with FRED metrics (date, metric_name, series_id, value)
        properties_df: Optional DataFrame with property listings data

    Returns:
        Dictionary with keys as chart identifiers and values as HTML strings:
        - 'correlation_heatmap': Correlation matrix heatmap
        - 'price_vs_employment': Scatter plot of median price vs employment
        - 'price_vs_listings': Scatter plot of median price vs active listings
        - 'dom_vs_listings': Scatter plot of days on market vs active listings

        Returns empty chart messages if fred_df is empty
    """
    charts = {}

    # Generate correlation heatmap
    if not fred_df.empty:
        corr_matrix = calculate_correlations(fred_df)
        charts["correlation_heatmap"] = create_correlation_heatmap(corr_matrix)
    else:
        fig = go.Figure()
        fig.add_annotation(
            text="No FRED data available. Please run 'python app.py' to populate the database.",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=14, color="gray"),
        )
        fig.update_layout(
            title="FRED Metrics Correlation Heatmap", template="plotly_white", height=500
        )
        charts["correlation_heatmap"] = fig.to_html(full_html=False, include_plotlyjs=False)

    # Generate scatter plots for key relationships
    if not fred_df.empty:
        # Price vs Employment
        html, corr, p_val = create_scatter_with_trendline(
            fred_df, "employment_non_farm", "median_price"
        )
        charts["price_vs_employment"] = html

        # Price vs Active Listings
        html, corr, p_val = create_scatter_with_trendline(
            fred_df, "active_listings", "median_price"
        )
        charts["price_vs_listings"] = html

        # Days on Market vs Active Listings
        html, corr, p_val = create_scatter_with_trendline(fred_df, "active_listings", "median_dom")
        charts["dom_vs_listings"] = html
    else:
        # Create empty charts with messages
        for chart_key, title in [
            ("price_vs_employment", "Median Price vs Employment"),
            ("price_vs_listings", "Median Price vs Active Listings"),
            ("dom_vs_listings", "Days on Market vs Active Listings"),
        ]:
            fig = go.Figure()
            fig.add_annotation(
                text="No FRED data available. Please run 'python app.py' to populate the database.",
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                showarrow=False,
                font=dict(size=14, color="gray"),
            )
            fig.update_layout(title=title, template="plotly_white", height=400)
            charts[chart_key] = fig.to_html(full_html=False, include_plotlyjs=False)

    return charts


if __name__ == "__main__":
    # Test with sample data
    import sqlite3
    import os

    # Try to read from database if it exists
    db_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "BNASFR02.DB"
    )

    if os.path.exists(db_path):
        print(f"Testing analytics with database: {db_path}")

        conn = sqlite3.connect(db_path)
        fred_df = pd.read_sql_query("SELECT * FROM BNA_FRED_METRICS", conn)
        conn.close()

        print(f"\nLoaded {len(fred_df)} FRED metric observations")

        # Test correlation calculation
        corr_matrix = calculate_correlations(fred_df)
        print(f"\nCorrelation matrix shape: {corr_matrix.shape}")
        print("\nCorrelation matrix:")
        print(corr_matrix)

        # Test dashboard creation
        charts = create_market_indicators_dashboard(fred_df)
        print(f"\nGenerated {len(charts)} charts:")
        for chart_name in charts.keys():
            print(f"  - {chart_name}")
    else:
        print(f"Database not found at: {db_path}")
        print("Run 'python app.py' first to populate the database")
