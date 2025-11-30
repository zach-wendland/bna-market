"""
Web utilities package for BNA Market application.

This package contains utility modules for the web dashboard:
- map_generator: Interactive map visualizations for property data
- analytics: Market analytics and correlation analysis tools
"""

from .map_generator import create_property_map, create_price_heatmap
from .analytics import (
    calculate_correlations,
    create_correlation_heatmap,
    create_scatter_with_trendline,
    create_market_indicators_dashboard
)

__all__ = [
    'create_property_map',
    'create_price_heatmap',
    'calculate_correlations',
    'create_correlation_heatmap',
    'create_scatter_with_trendline',
    'create_market_indicators_dashboard'
]
