# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

BNA Market is a Nashville real estate market analytics application. It collects property listings from Zillow and economic indicators from FRED, stores them in Supabase PostgreSQL, and visualizes them via a Flask API + Vue.js frontend.

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
pytest                                    # All tests with coverage
pytest tests/unit/test_api_routes.py -v   # Single file
pytest -k "test_health" -v                # Single test by name

# Code quality
black bna_market tests
flake8 bna_market
mypy bna_market
```

## Architecture

### Python Package (`bna_market/`)
- `core/config.py` - Configuration and Supabase settings
- `pipelines/` - ETL pipelines (Zillow for-sale, rentals, FRED metrics)
- `services/etl_service.py` - ETL orchestration
- `utils/database.py` - Supabase client and PostgreSQL connection
- `utils/` - Logging, retry utilities
- `web/app.py` - Flask application factory
- `web/api/routes.py` - REST API endpoints

### Vue Frontend (`frontend/`)
- `src/api/client.ts` - Axios API client
- `src/stores/dashboard.ts` - Pinia state management
- `src/components/` - Vue components (properties, maps, filters)
- `src/composables/` - Shared composables

### Data Flow
```
Zillow/FRED APIs → Python ETL → Supabase PostgreSQL → Flask API → Vue Frontend
```

## Database (Supabase PostgreSQL)

Tables (lowercase for PostgreSQL):
- `bna_forsale` - For-sale properties (unique on `zpid`)
- `bna_rentals` - Rental properties (unique on `zpid`)
- `bna_fred_metrics` - Economic indicators (unique on `date` + `series_id`)

## Environment

Required in `.env` (and Vercel environment variables):
```
RAPID_API_KEY=your_rapidapi_key
FRED_API_KEY=your_fred_api_key
SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_supabase_service_key
```

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/health` | Health check |
| `GET /api/dashboard` | Full dashboard data (KPIs, properties, metrics) |
| `GET /api/properties/search` | Search with filters and pagination |
| `GET /api/properties/export` | Export as CSV |
| `GET /api/metrics/fred` | FRED economic data |

## Deployment

**Vercel Deployment:**
- Entrypoint: `api/index.py` (exposes Flask `app` variable)
- Config: `vercel.json` - DO NOT specify Python runtime (auto-detects Python 3.12)
- Frontend builds to `frontend/dist/`
- API rewrites: `/api/*` → `api/index.py`, all other routes → SPA

**Required Vercel Environment Variables:**
- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`
- `SUPABASE_SERVICE_KEY`
- `RAPID_API_KEY` (for ETL only)
- `FRED_API_KEY` (for ETL only)

## Testing

Tests in `tests/` use pytest with fixtures in `conftest.py`:
- `temp_db` - Test database fixtures
- `flask_test_client` - Flask test client
- `mock_requests_get`, `mock_fred_api` - API mocking

Coverage target: 80%
