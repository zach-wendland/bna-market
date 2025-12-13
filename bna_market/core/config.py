"""
Centralized configuration for BNA Market application

This module consolidates all configuration settings including:
- Environment variables (via python-dotenv)
- Geographic boundaries (Nashville polygon)
- Zillow API search filters
- FRED economic indicator series IDs
- Database settings

Usage:
    from bna_market.core.config import settings, ZILLOW_CONFIG, DATABASE_CONFIG

    api_key = settings["rapid_api_key"]
    db_path = DATABASE_CONFIG["path"]
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base directory for resolving relative paths (project root - 3 levels up from this file)
# bna_market/core/config.py -> project root
BASE_DIR = Path(__file__).resolve().parent.parent.parent


# Settings dictionary (environment variables)
settings = {
    # API Keys (required for ETL)
    "rapid_api_key": os.getenv("RAPID_API_KEY", ""),
    "fred_api_key": os.getenv("FRED_API_KEY", ""),

    # Supabase configuration (required for database operations)
    "supabase_url": os.getenv("SUPABASE_URL", ""),
    "supabase_anon_key": os.getenv("SUPABASE_ANON_KEY", ""),
    "supabase_service_key": os.getenv("SUPABASE_SERVICE_KEY", ""),
    "supabase_jwt_secret": os.getenv("SUPABASE_JWT_SECRET", ""),  # JWT secret for verifying auth tokens
    # Database password for direct PostgreSQL/pooler connections (NOT the service key)
    "supabase_db_password": os.getenv("SUPABASE_DB_PASSWORD", ""),
    # Pooler host varies by region (us-west-2, us-east-1, eu-central-1, etc.)
    "supabase_pooler_host": os.getenv("SUPABASE_POOLER_HOST", "aws-0-us-west-2.pooler.supabase.com"),
}


# Geographic boundaries for Nashville, TN metropolitan area
NASHVILLE_POLYGON = {
    "west": -87.2316,
    "north": 36.5227,
    "east": -86.3316,
    "south": 35.8027,
}


# Zillow API configuration
ZILLOW_CONFIG = {
    "for_sale": {
        "minPrice": 100000,
        "maxPrice": 700000,
        "bedsMin": 1,
        "bedsMax": 5,
        "bathsMin": 1,
        "bathsMax": 4,
        "sqftMin": 700,
        "sqftMax": 5000,
        "buildYearMin": 1990,
        "max_pages": 20,
        "page_delay": 0.5,
    },
    "rentals": {
        "minPrice": 1400,
        "maxPrice": 3200,
        "bedsMin": 1,
        "bedsMax": 4,
        "bathsMin": 1,
        "bathsMax": 4,
        "sqftMin": 550,
        "sqftMax": 6000,
        "buildYearMin": 1979,
        "max_pages": 20,
        "page_delay": 0.5,
    },
}


# FRED API configuration
# 12 Nashville MSA Economic Indicators for December 2025 socioeconomic analysis
# Data range: 2023-present (2 years of historical data)
FRED_CONFIG = {
    "series_ids": {
        # Housing Market Indicators
        "median_price": "MEDLISPRI34980",           # Median Listing Price - Nashville MSA
        "active_listings": "ACTLISCOU34980",         # Active Listing Count - Nashville MSA
        "median_dom": "MEDDAYONMAR34980",            # Median Days on Market - Nashville MSA
        "median_pp_sqft": "MEDLISPRIPERSQUFEE34980", # Median Listing Price per Sq Ft - Nashville MSA

        # Employment & Economy
        "unemployment_rate": "NASH947URN",           # Unemployment Rate - Nashville MSA
        "employment": "NASH947NA",                   # All Employees: Total Nonfarm - Nashville MSA

        # Construction Activity
        "building_permits": "NASH947BPPRIVSA",       # Building Permits - Nashville MSA

        # Financing
        "mortgage_rate_30yr": "MORTGAGE30US",        # 30-Year Fixed Rate Mortgage Average (National)

        # Rental Market
        "rental_vacancy": "RRVRUSQ156N",             # Rental Vacancy Rate (National - proxy)

        # Income & Demographics
        "per_capita_income": "NASH947PCPI",          # Per Capita Personal Income - Nashville MSA
        "population": "NVLPOP",                      # Population - Nashville MSA

        # Market Confidence
        "consumer_sentiment": "UMCSENT",             # Consumer Sentiment Index (National)
    },
    "years_historical": 2,  # 2023-present for compact charts
}


# Supabase configuration
SUPABASE_CONFIG = {
    "url": settings["supabase_url"],
    "anon_key": settings["supabase_anon_key"],
    "service_key": settings["supabase_service_key"],
}


# Database configuration (table names use lowercase for PostgreSQL)
DATABASE_CONFIG = {
    "tables": {
        "for_sale": "bna_forsale",
        "rentals": "bna_rentals",
        "fred_metrics": "bna_fred_metrics",
    },
    "unique_keys": {
        # zpid + snapshot_date allows same property on different days (historical tracking)
        "for_sale": ["zpid", "snapshot_date"],
        "rentals": ["zpid", "snapshot_date"],
        "fred_metrics": ["date", "series_id"],
    },
}
