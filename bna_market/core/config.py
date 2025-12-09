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
FRED_CONFIG = {
    "series_ids": {
        "active_listings": "ACTLISCOU34980",
        "median_price": "MEDLISPRI34980",
        "median_dom": "MEDDAYONMAR34980",
        "employment_non_farm": "NASH947NA",
        "msa_population": "NVLPOP",
        "median_pp_sqft": "MEDLISPRIPERSQUFEE34980",
        "median_listing_price_change": "MEDLISPRI34980",
        "msa_per_capita_income": "NASH947PCPI",
    },
    "years_historical": 15,
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
        "for_sale": ["zpid"],
        "rentals": ["zpid"],
        "fred_metrics": ["date", "series_id"],
    },
}
