# BNA Market - Nashville Real Estate Analytics

A real estate market analytics dashboard for Nashville, TN featuring property listings from Zillow and economic indicators from FRED.

## Tech Stack

- **Frontend**: Vue 3 + Vite + Tailwind CSS + Chart.js
- **Backend**: Flask API (Python 3.12)
- **Database**: Supabase (PostgreSQL)
- **Deployment**: Vercel (serverless)

## Features

- Interactive property map with Leaflet.js
- Sortable data tables with filtering
- Price per square foot calculations
- Real-time filter preview
- CSV export
- FRED economic metrics charts

## Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+
- [Supabase](https://supabase.com) account (free tier works)
- [Zillow RapidAPI](https://rapidapi.com/apimaker/api/zillow-com1) key
- [FRED API](https://fred.stlouisfed.org/docs/api/api_key.html) key

### Installation

```bash
# Clone and install Python deps
git clone <repo-url>
cd bna-market
pip install -e ".[dev]"

# Install frontend deps
cd frontend && npm install
```

### Environment Variables

Create `.env` in project root:

```bash
# Database (required)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_KEY=your_service_key

# ETL API Keys (required for data collection)
RAPID_API_KEY=your_rapidapi_key
FRED_API_KEY=your_fred_api_key
```

### Supabase Setup

Create these tables in your Supabase project:

```sql
-- For-sale properties
CREATE TABLE bna_forsale (
  id SERIAL PRIMARY KEY,
  zpid TEXT UNIQUE NOT NULL,
  address TEXT,
  city TEXT,
  state TEXT,
  zip_code TEXT,
  price NUMERIC,
  bedrooms INTEGER,
  bathrooms NUMERIC,
  living_area NUMERIC,
  latitude NUMERIC,
  longitude NUMERIC,
  property_type TEXT,
  home_status TEXT,
  date_sold TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Rental properties
CREATE TABLE bna_rentals (
  id SERIAL PRIMARY KEY,
  zpid TEXT UNIQUE NOT NULL,
  address TEXT,
  city TEXT,
  state TEXT,
  zip_code TEXT,
  price NUMERIC,
  bedrooms INTEGER,
  bathrooms NUMERIC,
  living_area NUMERIC,
  latitude NUMERIC,
  longitude NUMERIC,
  property_type TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

-- FRED economic metrics
CREATE TABLE bna_fred_metrics (
  id SERIAL PRIMARY KEY,
  date DATE NOT NULL,
  series_id TEXT NOT NULL,
  value NUMERIC,
  created_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(date, series_id)
);
```

### Development

```bash
# Run ETL to populate database
python -m bna_market etl run

# Start Flask API (port 5000)
python -m bna_market web serve

# Start Vue dev server (port 5173) - in another terminal
cd frontend && npm run dev
```

## Vercel Deployment

### Critical Configuration

The `vercel.json` uses auto-detected Python 3.12:

```json
{
  "buildCommand": "cd frontend && npm install && npm run build",
  "outputDirectory": "frontend/dist",
  "functions": {
    "api/*.py": {
      "maxDuration": 60
    }
  },
  "rewrites": [
    { "source": "/api/:path*", "destination": "/api/index.py" },
    { "source": "/(.*)", "destination": "/index.html" }
  ]
}
```

> **WARNING**: Do NOT add `"runtime"` to vercel.json. Vercel only supports Python 3.12 which is auto-detected. Specifying any runtime causes `spawn pip3.x ENOENT` errors.

### Required Vercel Environment Variables

Add these in Vercel Dashboard → Settings → Environment Variables:

| Variable | Required | Description |
|----------|----------|-------------|
| `SUPABASE_URL` | Yes | Your Supabase project URL |
| `SUPABASE_ANON_KEY` | Yes | Supabase anonymous/public key |
| `SUPABASE_SERVICE_KEY` | Yes | Supabase service role key |
| `RAPID_API_KEY` | For ETL | Zillow RapidAPI key |
| `FRED_API_KEY` | For ETL | FRED API key |

### Deploy Steps

1. Push to GitHub
2. Import project in Vercel
3. Add environment variables (above)
4. Deploy

### Verify Deployment

```bash
# Health check (should return JSON)
curl https://your-app.vercel.app/api/health

# Dashboard data (requires Supabase env vars)
curl https://your-app.vercel.app/api/dashboard
```

## Project Structure

```
bna-market/
├── api/index.py              # Vercel serverless entrypoint
├── bna_market/               # Python package
│   ├── core/config.py        # Configuration + Supabase settings
│   ├── pipelines/            # ETL pipelines (Zillow, FRED)
│   ├── services/etl_service.py
│   ├── utils/                # Database, logging, retry
│   └── web/                  # Flask API
│       ├── app.py
│       └── api/routes.py
├── frontend/                 # Vue.js SPA
│   └── src/
│       ├── api/              # Axios client
│       ├── components/       # Vue components
│       ├── composables/      # Vue composables
│       └── stores/           # Pinia stores
├── tests/                    # Python tests
├── requirements.txt          # Python dependencies (for Vercel)
├── pyproject.toml            # Python package config
└── vercel.json               # Vercel deployment config
```

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/health` | Health check |
| `GET /api/dashboard` | Full dashboard data (KPIs, properties, metrics) |
| `GET /api/properties/search` | Search properties with filters |
| `GET /api/properties/export` | Export as CSV |
| `GET /api/metrics/fred` | FRED economic metrics |

### Search Parameters

- `property_type`: 'forsale' or 'rental' (required)
- `min_price`, `max_price`: Price range
- `min_beds`, `max_beds`: Bedroom count
- `min_baths`, `max_baths`: Bathroom count
- `min_sqft`, `max_sqft`: Square footage
- `city`, `zip_code`: Location filters
- `sort_by`, `sort_order`: Sorting
- `page`, `per_page`: Pagination (max 100)

## Database Schema

Supabase PostgreSQL tables (lowercase):

| Table | Purpose | Unique Key |
|-------|---------|------------|
| `bna_forsale` | For-sale properties | `zpid` |
| `bna_rentals` | Rental properties | `zpid` |
| `bna_fred_metrics` | Economic indicators | `date` + `series_id` |

## Testing

```bash
pytest                                    # All tests with coverage
pytest tests/unit/test_api_routes.py -v   # Single file
pytest -k "test_health" -v                # Single test by name
```

## License

MIT
