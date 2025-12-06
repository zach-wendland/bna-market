# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

BNA Market is a Nashville real estate market analytics application that collects property listings from Zillow and economic indicators from FRED, stores them in SQLite, and visualizes them in a Flask dashboard with Plotly charts.

**Geographic Focus**: Nashville, TN metropolitan area (polygon: -87.2316 36.5227 to -86.3316 35.8027)

## Development Commands

```bash
# Run ETL pipeline (fetch data and update database)
python -m bna_market etl run

# Start web server
python -m bna_market web serve

# Run tests with coverage
pytest

# Run single test file
pytest tests/unit/test_api_routes.py

# Run specific test
pytest tests/unit/test_api_routes.py::test_search_properties_success -v

# Format code
black bna_market tests

# Type checking
mypy bna_market

# Linting
flake8 bna_market
```

## Architecture

### Package Structure
```
bna_market/
├── core/config.py       # Centralized settings (API keys, search filters, DB path)
├── services/etl_service.py  # ETL orchestration with deduplication
├── pipelines/           # Data collection
│   ├── zillow_base.py   # Shared Zillow API logic with retry
│   ├── for_sale.py      # For-sale properties
│   ├── rental.py        # Rental properties
│   └── fred_metrics.py  # FRED economic indicators
├── web/
│   ├── app.py           # Flask application factory (create_app)
│   └── api/routes.py    # REST API endpoints
└── utils/               # Shared utilities (logger, database, retry, validators)
```

### Data Flow
1. **Pipelines** fetch from Zillow/FRED APIs with retry logic
2. **ETLService** merges new data with existing, deduplicates, and updates SQLite
3. **Flask app** reads from SQLite, renders Plotly charts + API endpoints

### Database Schema (BNASFR02.DB)
- `BNA_FORSALE` - For-sale properties (unique on `zpid`)
- `BNA_RENTALS` - Rental properties (unique on `zpid`)
- `BNA_FRED_METRICS` - Economic indicators (unique on `date` + `series_id`)

### Key Entry Points
- CLI: `bna_market/__main__.py` - argparse-based CLI
- ETL: `ETLService.run_full_refresh()` in `services/etl_service.py`
- Web: `create_app()` factory in `web/app.py`

## Environment Setup

Required in `.env`:
```
RAPID_API_KEY=<your-rapidapi-key>
FRED_API_KEY=<your-fred-api-key>
```

Optional:
```
DATABASE_PATH=BNASFR02.DB  # Defaults to project root
```

## Installation

```bash
# Development install (editable)
pip install -e .

# Or use requirements.txt
pip install -r requirements.txt
```

After installation, the `bna-market` CLI command becomes available:
```bash
bna-market etl run
bna-market web serve
```

## Deployment

Configured for multiple platforms:
- **Vercel**: Serverless via `api/index.py` entry point
- **Railway/Heroku/Render**: gunicorn with `bna_market.web.app:create_app()`

## Testing

Tests use pytest with fixtures in `tests/conftest.py`:
- `temp_db` - Creates temporary SQLite database with schema
- `sample_forsale_df`, `sample_rental_df`, `sample_fred_df` - Sample DataFrames
- `flask_test_client` - Flask test client for API testing
- `mock_requests_get`, `mock_fred_api` - API mocking

Coverage target: 80% (configured in pyproject.toml)

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/health` | Health check |
| `GET /api/properties/search` | Search properties (params: property_type, min_price, max_price, min_beds, etc.) |
| `GET /api/properties/export` | Export properties as CSV |
| `GET /api/metrics/fred` | Get FRED economic metrics |

## Common Patterns

### Database Access
```python
from bna_market.utils.database import get_db_connection, read_table_safely

with get_db_connection(db_path) as conn:
    df = read_table_safely("BNA_FORSALE", conn)
```

### Logging
```python
from bna_market.utils.logger import setup_logger
logger = setup_logger("module_name")
```

### Configuration
```python
from bna_market.core.config import settings, ZILLOW_CONFIG, DATABASE_CONFIG
api_key = settings["rapid_api_key"]
```

## API Rate Limits

**Zillow API** (via RapidAPI):
- 20 pages max per pipeline run
- 0.5 second delay between requests
- Retry with exponential backoff (3 retries)

**FRED API**:
- 8 series fetched sequentially
- 15 years of historical data per series

## Legacy Files

The root `app.py` is a deprecated wrapper maintained for backwards compatibility. Use the CLI commands instead:
```bash
# Old (deprecated)
python app.py

# New (preferred)
python -m bna_market etl run
```

## UI/UX Improvement Plan

Comprehensive plan for dashboard improvements located at:
`C:\Users\lyyud\.claude\plans\cozy-dazzling-raccoon.md`

**Phase 1 (Critical)**: Map view, unified filters, table sorting, price/sqft, real-time feedback
**Phase 2 (Important)**: Filter chips, performance fixes (iterrows→to_dict), data freshness, advanced filters

All recommendations validated with 2024-2025 research from Realtor.com, Nielsen Norman Group, WCAG 2.1, and performance benchmarks.
