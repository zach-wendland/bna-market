# BNA Market - Nashville Real Estate Analytics

A real estate market analytics dashboard for Nashville, TN featuring property listings from Zillow and economic indicators from FRED.

## Tech Stack

- **Frontend**: Vue 3 + Vite + Tailwind CSS + Pinia
- **Backend**: Flask API (Python)
- **Database**: SQLite
- **Deployment**: Vercel

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
- Zillow RapidAPI key
- FRED API key

### Installation

```bash
# Clone and install Python deps
git clone <repo-url>
cd bna-market
pip install -e ".[dev]"

# Install frontend deps
cd frontend && npm install
```

### Environment

Create `.env` in project root:
```
RAPID_API_KEY=your_rapidapi_key
FRED_API_KEY=your_fred_api_key
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

### Production Build

```bash
cd frontend && npm run build
# Deploy to Vercel or serve with Flask
```

## Project Structure

```
bna-market/
├── api/index.py              # Vercel entrypoint
├── bna_market/               # Python package
│   ├── core/config.py        # Configuration
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
├── pyproject.toml            # Python config
└── vercel.json               # Vercel config
```

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/health` | Health check |
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

## Database

SQLite database (`BNASFR02.DB`) with tables:
- `BNA_FORSALE` - For-sale properties
- `BNA_RENTALS` - Rental properties
- `BNA_FRED_METRICS` - Economic indicators

## Testing

```bash
pytest                           # Run all tests
pytest tests/unit/test_api.py   # Single file
pytest -v -k "test_health"      # Specific test
```

## License

MIT
