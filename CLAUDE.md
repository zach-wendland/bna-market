# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

BNA Market is a Nashville real estate market analytics application. It collects property listings from Zillow and economic indicators from FRED, stores them in SQLite, and visualizes them via a Flask API + Vue.js frontend.

## Development Commands

```bash
# Install Python dependencies
pip install -e ".[dev]"

# Install frontend dependencies
cd frontend && npm install

# Run ETL pipeline (populates database)
python -m bna_market etl run

# Start Flask API server (port 5000)
python -m bna_market web serve

# Start Vue dev server (port 5173)
cd frontend && npm run dev

# Run tests
pytest
pytest tests/unit/test_api_routes.py -v

# Code quality
black bna_market tests
flake8 bna_market
mypy bna_market
```

## Architecture

### Python Package (`bna_market/`)
- `core/config.py` - Configuration and settings
- `pipelines/` - ETL pipelines (Zillow for-sale, rentals, FRED metrics)
- `services/etl_service.py` - ETL orchestration
- `utils/` - Database, logging, retry utilities
- `web/app.py` - Flask application factory
- `web/api/routes.py` - REST API endpoints

### Vue Frontend (`frontend/`)
- `src/api/client.ts` - Axios API client
- `src/stores/dashboard.ts` - Pinia state management
- `src/components/` - Vue components (properties, maps, filters)
- `src/composables/` - Shared composables

### Data Flow
```
Zillow/FRED APIs → Python ETL → SQLite → Flask API → Vue Frontend
```

## Database (BNASFR02.DB)

- `BNA_FORSALE` - For-sale properties (unique on `zpid`)
- `BNA_RENTALS` - Rental properties (unique on `zpid`)
- `BNA_FRED_METRICS` - Economic indicators (unique on `date` + `series_id`)

## Environment

Required in `.env`:
```
RAPID_API_KEY=your_rapidapi_key
FRED_API_KEY=your_fred_api_key
```

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/health` | Health check |
| `GET /api/properties/search` | Search with filters |
| `GET /api/properties/export` | Export as CSV |
| `GET /api/metrics/fred` | FRED economic data |

## Deployment

Vercel deployment via `api/index.py` + `vercel.json`. Frontend builds to `frontend/dist/`.

## Testing

Tests in `tests/` use pytest with fixtures in `conftest.py`:
- `temp_db` - Temporary SQLite database
- `flask_test_client` - Flask test client
- `mock_requests_get`, `mock_fred_api` - API mocking

Coverage target: 80%
