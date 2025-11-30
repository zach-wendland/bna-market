"""
Centralized configuration for BNA Market application

This module contains all configuration settings including:
- Geographic boundaries (Nashville polygon)
- Zillow API search filters
- FRED economic indicator series IDs
- Database settings
"""

# Geographic boundaries for Nashville, TN metropolitan area
NASHVILLE_POLYGON = {
    'west': -87.2316,
    'north': 36.5227,
    'east': -86.3316,
    'south': 35.8027
}

# Zillow API configuration
ZILLOW_CONFIG = {
    'for_sale': {
        'minPrice': 100000,
        'maxPrice': 700000,
        'bedsMin': 1,
        'bedsMax': 5,
        'bathsMin': 1,
        'bathsMax': 4,
        'sqftMin': 700,
        'sqftMax': 5000,
        'buildYearMin': 1990,
        'max_pages': 20,
        'page_delay': 0.5
    },
    'rentals': {
        'minPrice': 1400,
        'maxPrice': 3200,
        'bedsMin': 1,
        'bedsMax': 4,
        'bathsMin': 1,
        'bathsMax': 4,
        'sqftMin': 550,
        'sqftMax': 6000,
        'buildYearMin': 1979,
        'max_pages': 20,
        'page_delay': 0.5
    }
}

# FRED API configuration
FRED_CONFIG = {
    'series_ids': {
        'active_listings': 'ACTLISCOU34980',
        'median_price': 'MEDLISPRI34980',
        'median_dom': 'MEDDAYONMAR34980',
        'employment_non_farm': 'NASH947NA',
        'msa_population': 'NVLPOP',
        'median_pp_sqft': 'MEDLISPRIPERSQUFEE34980',
        'median_listing_price_change': 'MEDLISPRI34980',
        'msa_per_capita_income': 'NASH947PCPI'
    },
    'years_historical': 15
}

# Database configuration
DATABASE_CONFIG = {
    'path': 'BNASFR02.DB',
    'tables': {
        'for_sale': 'BNA_FORSALE',
        'rentals': 'BNA_RENTALS',
        'fred_metrics': 'BNA_FRED_METRICS'
    },
    'unique_keys': {
        'for_sale': ['zpid'],
        'rentals': ['zpid'],
        'fred_metrics': ['date', 'series_id']
    }
}
