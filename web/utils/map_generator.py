"""
Map generation utilities for BNA Market dashboard.

This module provides functions to create interactive Plotly maps for property data:
- Scatter maps showing individual property locations
- Density heatmaps showing price concentration areas
"""

import pandas as pd
import plotly.express as px


def create_property_map(df, property_type):
    """
    Create an interactive scatter map of property locations.

    Args:
        df (pd.DataFrame): Property data with latitude, longitude, and property details
        property_type (str): Type of property ('for-sale' or 'rental')

    Returns:
        str: HTML string of the Plotly map figure
    """
    # Handle empty DataFrame
    if df is None or df.empty:
        return f"<div class='empty-state'>No {property_type} property data available for mapping</div>"

    # Filter out rows with missing coordinates
    df_filtered = df.dropna(subset=['latitude', 'longitude'])

    if df_filtered.empty:
        return f"<div class='empty-state'>No {property_type} properties with valid coordinates</div>"

    # Prepare hover text based on property type
    if property_type == 'for-sale':
        df_filtered = df_filtered.copy()
        df_filtered['hover_text'] = df_filtered.apply(
            lambda row: (
                f"<b>{row.get('address', 'N/A')}</b><br>"
                f"Price: ${row.get('price', 0):,.0f}<br>"
                f"Beds: {row.get('bedrooms', 'N/A')} | Baths: {row.get('bathrooms', 'N/A')}<br>"
                f"Size: {row.get('livingArea', 'N/A'):,.0f} sqft<br>"
                f"Built: {row.get('yearBuilt', 'N/A')}"
            ),
            axis=1
        )
        color_col = 'price'
        color_label = 'Price ($)'
    else:  # rental
        df_filtered = df_filtered.copy()
        df_filtered['hover_text'] = df_filtered.apply(
            lambda row: (
                f"<b>{row.get('address', 'N/A')}</b><br>"
                f"Rent: ${row.get('price', 0):,.0f}/mo<br>"
                f"Beds: {row.get('beds', 'N/A')} | Baths: {row.get('baths', 'N/A')}<br>"
                f"Size: {row.get('area', 'N/A'):,.0f} sqft"
            ),
            axis=1
        )
        color_col = 'price'
        color_label = 'Monthly Rent ($)'

    # Create scatter mapbox
    fig = px.scatter_mapbox(
        df_filtered,
        lat='latitude',
        lon='longitude',
        color=color_col,
        hover_name='hover_text',
        color_continuous_scale='Viridis',
        zoom=9.5,
        height=600,
        labels={color_col: color_label}
    )

    # Update layout
    fig.update_layout(
        mapbox_style="open-street-map",
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="Arial"
        )
    )

    # Update hover template to only show the custom hover text
    fig.update_traces(
        hovertemplate='%{hovertext}<extra></extra>',
        hovertext=df_filtered['hover_text']
    )

    # Return HTML with CDN for plotly.js (first map on page)
    return fig.to_html(full_html=False, include_plotlyjs='cdn')


def create_price_heatmap(df, property_type):
    """
    Create a density heatmap showing price concentration areas.

    Args:
        df (pd.DataFrame): Property data with latitude, longitude, and price
        property_type (str): Type of property ('for-sale' or 'rental')

    Returns:
        str: HTML string of the Plotly density map figure
    """
    # Handle empty DataFrame
    if df is None or df.empty:
        return f"<div class='empty-state'>No {property_type} property data available for heatmap</div>"

    # Filter out rows with missing coordinates or price
    df_filtered = df.dropna(subset=['latitude', 'longitude', 'price'])

    if df_filtered.empty:
        return f"<div class='empty-state'>No {property_type} properties with valid coordinates and prices</div>"

    # Prepare hover text based on property type
    if property_type == 'for-sale':
        df_filtered = df_filtered.copy()
        df_filtered['hover_text'] = df_filtered.apply(
            lambda row: (
                f"<b>{row.get('address', 'N/A')}</b><br>"
                f"Price: ${row.get('price', 0):,.0f}"
            ),
            axis=1
        )
        z_col = 'price'
        color_label = 'Price Density'
    else:  # rental
        df_filtered = df_filtered.copy()
        df_filtered['hover_text'] = df_filtered.apply(
            lambda row: (
                f"<b>{row.get('address', 'N/A')}</b><br>"
                f"Rent: ${row.get('price', 0):,.0f}/mo"
            ),
            axis=1
        )
        z_col = 'price'
        color_label = 'Rent Density'

    # Create density mapbox
    fig = px.density_mapbox(
        df_filtered,
        lat='latitude',
        lon='longitude',
        z=z_col,
        radius=15,
        zoom=9.5,
        height=600,
        color_continuous_scale='Hot',
        labels={z_col: color_label}
    )

    # Update layout
    fig.update_layout(
        mapbox_style="open-street-map",
        margin={"r": 0, "t": 0, "l": 0, "b": 0}
    )

    # Return HTML without plotly.js (subsequent map on page)
    return fig.to_html(full_html=False, include_plotlyjs=False)
