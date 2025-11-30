# BNA Market - Nashville Real Estate Analytics

Real estate market analytics application for Nashville, TN metropolitan area.
Collects property listings from Zillow and economic indicators from FRED, stores in SQLite, and visualizes in Flask dashboard.

## Features

- **Property Listings**: For-sale and rental properties from Zillow API
- **Economic Indicators**: 8 FRED metrics (employment, population, median prices, etc.)
- **Interactive Dashboard**: Plotly charts, property tables, search/filtering
- **Geographic Visualization**: Interactive property maps with price heatmaps
- **Market Analytics**: Correlation analysis, trend charts, market indicators
- **Data Export**: Download filtered properties as CSV
- **REST API**: Search and export endpoints for programmatic access

## Quick Start

### Prerequisites

- Python 3.8+
- Zillow RapidAPI key ([Get one here](https://rapidapi.com/))
- FRED API key ([Get one here](https://fred.stlouisfed.org/docs/api/api_key.html))

### Installation

1. Clone repository:
```bash
git clone <repo-url>
cd bna-market
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env and add your API keys:
# RAPID_API_KEY=your_rapidapi_key_here
# FRED_API_KEY=your_fred_api_key_here
```

4. Run ETL pipeline to populate database:
```bash
python app.py
```

5. Launch dashboard:
```bash
cd web
python web_app.py
```

6. Open browser to http://127.0.0.1:5000

## Project Structure

```
bna-market/
├── pipelines/           # Data collection pipelines
│   ├── zillow_base.py   # Shared Zillow API logic
│   ├── forSale.py       # For-sale properties pipeline
│   ├── rentalPipe.py    # Rental properties pipeline
│   └── otherMetricsPipe.py  # FRED economic indicators
├── web/                 # Flask web application
│   ├── web_app.py       # Main Flask app
│   ├── api/             # REST API endpoints
│   ├── templates/       # Jinja2 templates
│   ├── static/          # CSS, JS, images
│   └── utils/           # Map generation, analytics
├── utils/               # Shared utilities
│   ├── logger.py        # Logging configuration
│   ├── database.py      # Database helpers
│   ├── validators.py    # Data validation
│   ├── retry.py         # Retry logic with backoff
│   ├── exceptions.py    # Custom exceptions
│   └── env_validator.py # Environment validation
├── config/              # Configuration files
│   └── settings.py      # Centralized settings
├── scripts/             # Utility scripts
│   └── add_indexes.py   # Database index creation
├── app.py               # ETL orchestration
├── BNASFR02.DB          # SQLite database
└── requirements.txt     # Python dependencies
```

## Configuration

Edit `config/settings.py` to modify:
- Geographic boundaries (Nashville polygon)
- Zillow search filters (price, beds, baths, sqft)
- FRED series IDs
- Database settings

## API Endpoints

### Search Properties
```
GET /api/properties/search
Query params: property_type, min_price, max_price, min_beds, max_beds, city, zip, page, per_page
```

### Export Properties
```
GET /api/properties/export
Returns CSV file with filtered properties
```

### FRED Metrics
```
GET /api/metrics/fred
Query params: metric_name, series_id, start_date, end_date
```

See [API Documentation](web/api/README.md) for complete details.

## Database Schema

### BNA_FORSALE
- Primary key: `zpid`
- Columns: price, address, bedrooms, bathrooms, livingArea, latitude, longitude, etc.

### BNA_RENTALS
- Primary key: `zpid`
- Columns: price, address, bedrooms, bathrooms, livingArea, units (JSON), etc.

### BNA_FRED_METRICS
- Composite key: `date` + `series_id`
- Columns: date, metric_name, series_id, value

## Development

### Running Tests
```bash
pytest tests/
```

### Manual Pipeline Testing
```bash
# Test individual pipelines
python pipelines/forSale.py
python pipelines/rentalPipe.py
python pipelines/otherMetricsPipe.py
```

### Add Database Indexes
```bash
python scripts/add_indexes.py
```

## Architecture

### Data Flow
1. **Data Collection** (`pipelines/`) → Fetch data from external APIs
2. **Data Storage** (`app.py`) → Transform and load into SQLite database
3. **Data Visualization** (`web/web_app.py`) → Flask dashboard with Plotly charts

### Key Components

- **Centralized Configuration** (`config/settings.py`): All hardcoded values moved to configuration
- **Structured Logging** (`utils/logger.py`): All operations logged with timestamps
- **Error Handling** (`utils/exceptions.py`): Custom exception hierarchy
- **Database Operations** (`utils/database.py`): Context managers for safe database access
- **Data Validation** (`utils/validators.py`): Input validation and data quality checks
- **Retry Logic** (`utils/retry.py`): Exponential backoff for API calls

## Recent Enhancements

### Code Quality Improvements
- ✅ Eliminated 95% code duplication in pipelines
- ✅ Replaced all print() statements with structured logging
- ✅ Replaced bare except clauses with specific exception handling
- ✅ Centralized configuration (no hardcoded values)
- ✅ Added retry logic with exponential backoff
- ✅ Implemented data validation layer
- ✅ Added environment variable validation

### New Features
- ✅ Interactive property maps (scatter maps & heatmaps)
- ✅ Market analytics with correlation analysis
- ✅ Advanced search & filtering API
- ✅ CSV export functionality
- ✅ Comprehensive documentation

## License

MIT License

## Contributing

Contributions welcome! Please read contributing guidelines before submitting pull requests.

## Support

For issues and questions:
- Open an issue on GitHub
- Check [API Documentation](web/api/README.md)
- Review [CLAUDE.md](CLAUDE.md) for development guidelines
