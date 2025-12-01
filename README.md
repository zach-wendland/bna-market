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

# API Implementation Summary

## Overview
Successfully created a Flask API blueprint for the BNA Market application with RESTful endpoints for property search, export, and economic metrics retrieval.

## Files Created

### 1. `web/api/__init__.py`
- Blueprint initialization file
- Registers the API blueprint with URL prefix `/api`
- Imports routes module

### 2. `web/api/routes.py` (Main implementation - 450+ lines)
- **Endpoint 1: `/api/properties/search`** (GET)
  - Search properties with comprehensive filters
  - Supports both 'forsale' and 'rental' property types
  - Filters: price range, beds, baths, square footage, city, zip code
  - Pagination: page and per_page parameters (max 100 items per page)
  - Returns JSON with properties array and pagination metadata
  - Uses parameterized SQL queries for security

- **Endpoint 2: `/api/properties/export`** (GET)
  - Export filtered properties as CSV file
  - Same filters as search endpoint (no pagination)
  - Returns downloadable CSV file
  - Proper Content-Type and Content-Disposition headers

- **Endpoint 3: `/api/metrics/fred`** (GET)
  - Get FRED economic metrics
  - Optional filters: metric_name, series_id, start_date, end_date
  - Returns JSON with metrics array and count
  - Ordered by date (descending) and metric name

- **Endpoint 4: `/api/health`** (GET)
  - Health check endpoint
  - Returns API status and available endpoints
  - Useful for monitoring and testing

**Key Features:**
- Uses `get_db_connection()` context manager from `utils/database.py`
- Implements proper error handling with `setup_logger()` from `utils/logger.py`
- Parameterized SQL queries to prevent SQL injection
- Comprehensive input validation
- Detailed logging for debugging and monitoring
- Standard HTTP status codes (200, 400, 500)

### 3. `web/api/README.md`
- Complete API documentation
- Endpoint descriptions with all parameters
- Example requests using curl, JavaScript, and Python
- Response format examples
- Error handling documentation
- Usage notes and best practices

### 4. `test_api.py` (Project Root)
- Comprehensive test suite for all API endpoints
- Tests include:
  - Health check
  - For-sale property search
  - Rental property search
  - FRED metrics retrieval
  - CSV export functionality
  - Error handling validation
- Provides detailed output and test summary
- Easy to run: `python test_api.py`

### 5. `utils/__init__.py`
- Created to make utils a proper Python package
- Required for imports to work correctly

## Integration with Existing Codebase

### Modified Files

#### `web/web_app.py`
Added API blueprint registration:
```python
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Register API blueprint
from web.api import api_bp
app.register_blueprint(api_bp)
```

## Database Schema Used

### BNA_FORSALE Table
Columns used in API:
- `zpid` - Unique property identifier
- `address` - Full address string
- `price` - Sale price
- `bedrooms` - Number of bedrooms
- `bathrooms` - Number of bathrooms
- `livingArea` - Square footage
- `propertyType` - Property type classification
- `latitude` / `longitude` - Geographic coordinates
- `imgSrc` - Image URL
- `detailUrl` - Zillow detail page URL
- `daysOnZillow` - Days listed
- `listingStatus` - Current status

### BNA_RENTALS Table
Same columns as BNA_FORSALE (uses same query structure)

### BNA_FRED_METRICS Table
Columns:
- `date` - Date of observation
- `metric_name` - Metric identifier
- `series_id` - FRED series ID
- `value` - Metric value

## How to Use

### Starting the API Server
From project root:
```bash
cd web
python web_app.py
```

Or:
```bash
python web/web_app.py
```

The API will be available at: `http://127.0.0.1:5000/api`

### Testing the API
1. Start the Flask app (see above)
2. In a new terminal, run the test suite:
   ```bash
   python test_api.py
   ```

### Example API Calls

**Search for-sale properties:**
```bash
curl "http://127.0.0.1:5000/api/properties/search?property_type=forsale&min_price=200000&max_price=400000&min_beds=2&page=1&per_page=20"
```

**Export rentals to CSV:**
```bash
curl "http://127.0.0.1:5000/api/properties/export?property_type=rental&min_price=1500&max_price=2500" -o rentals.csv
```

**Get FRED metrics:**
```bash
curl "http://127.0.0.1:5000/api/metrics/fred?metric_name=median_price&start_date=2023-01-01"
```

**Health check:**
```bash
curl "http://127.0.0.1:5000/api/health"
```

## Security Features

1. **Parameterized SQL Queries**: All database queries use parameter binding to prevent SQL injection
2. **Input Validation**: Type checking and validation for all query parameters
3. **Error Handling**: Comprehensive try-catch blocks with proper error messages
4. **Logging**: All requests and errors are logged for audit trail
5. **Pagination Limits**: Maximum 100 items per page to prevent resource exhaustion
6. **No Sensitive Data Exposure**: Error messages don't expose internal details

## Performance Considerations

1. **Database Connection Management**: Uses context managers for automatic connection cleanup
2. **Query Optimization**:
   - SELECT only needed columns (not SELECT *)
   - WHERE clauses built dynamically based on filters
   - ORDER BY for consistent results
3. **Pagination**: Prevents loading entire datasets into memory
4. **CSV Streaming**: Uses StringIO for efficient CSV generation

## Error Handling

All endpoints return consistent error responses:

**400 Bad Request:**
```json
{
  "error": "property_type must be either 'forsale' or 'rental'"
}
```

**500 Internal Server Error:**
```json
{
  "error": "Internal server error"
}
```

Detailed errors are logged but not exposed to clients for security.

## Logging

All API operations are logged with the 'api' logger:
- INFO: Successful operations with counts
- ERROR: Failed operations with details
- Logs written to `logs/api_YYYYMMDD.log`

## Dependencies

The API uses existing dependencies:
- `flask` - Web framework
- `sqlite3` - Database (standard library)
- `csv` - CSV handling (standard library)
- `io.StringIO` - In-memory CSV generation (standard library)

No new dependencies required.

## Future Enhancements

Potential improvements for future iterations:
1. **Authentication**: Add API key or JWT-based authentication
2. **Rate Limiting**: Implement request throttling
3. **Caching**: Add response caching for frequently requested data
4. **API Versioning**: Add version prefix (e.g., `/api/v1/`)
5. **OpenAPI/Swagger**: Generate interactive API documentation
6. **GraphQL**: Alternative query interface for complex data needs
7. **WebSocket**: Real-time updates for new listings
8. **Geospatial Queries**: Search within radius of coordinates
9. **Saved Searches**: User preference storage
10. **Bulk Operations**: Batch property updates/exports

## Testing Checklist

- [x] Health check endpoint works
- [x] Property search with filters works
- [x] Rental search with filters works
- [x] FRED metrics retrieval works
- [x] CSV export works
- [x] Pagination works correctly
- [x] Error handling for missing parameters
- [x] Error handling for invalid parameters
- [x] Logging captures all operations
- [x] SQL injection protection verified
- [x] Database connection cleanup verified

## Deployment Notes

For production deployment:
1. Set Flask debug mode to False
2. Use production WSGI server (gunicorn, uwsgi)
3. Add HTTPS/SSL
4. Implement authentication
5. Set up monitoring and alerting
6. Configure CORS if needed for web clients
7. Review and adjust rate limits
8. Set up database connection pooling
9. Implement request logging to external service

## Support

For issues or questions:
1. Check `web/api/README.md` for API documentation
2. Review `logs/api_YYYYMMDD.log` for error details
3. Run `python test_api.py` to verify endpoints
4. Check Flask console output for runtime errors

# BNA Market API Quick Start Guide

## Getting Started in 3 Steps

### Step 1: Start the Flask Application
```bash
# From project root
cd web
python web_app.py
```

You should see:
```
* Running on http://127.0.0.1:5000
```

### Step 2: Test the API
Open a new terminal and run:
```bash
# From project root
python test_api.py
```

Or test manually with curl:
```bash
curl http://127.0.0.1:5000/api/health
```

### Step 3: Try Some Queries

**Search for homes under $300k:**
```bash
curl "http://127.0.0.1:5000/api/properties/search?property_type=forsale&max_price=300000&per_page=5"
```

**Find 2+ bedroom rentals:**
```bash
curl "http://127.0.0.1:5000/api/properties/search?property_type=rental&min_beds=2&per_page=5"
```

**Export properties to CSV:**
```bash
curl "http://127.0.0.1:5000/api/properties/export?property_type=forsale&min_price=200000&max_price=400000" -o properties.csv
```

**Get economic metrics:**
```bash
curl "http://127.0.0.1:5000/api/metrics/fred?metric_name=median_price"
```

## Available Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/health` | API status check |
| `GET /api/properties/search` | Search properties with filters |
| `GET /api/properties/export` | Export properties to CSV |
| `GET /api/metrics/fred` | Get FRED economic data |

## Common Filters

### For `/api/properties/search` and `/api/properties/export`:

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `property_type` | string | **Required**: 'forsale' or 'rental' | `property_type=forsale` |
| `min_price` | float | Minimum price | `min_price=200000` |
| `max_price` | float | Maximum price | `max_price=500000` |
| `min_beds` | int | Minimum bedrooms | `min_beds=2` |
| `max_beds` | int | Maximum bedrooms | `max_beds=4` |
| `min_baths` | float | Minimum bathrooms | `min_baths=2` |
| `max_baths` | float | Maximum bathrooms | `max_baths=3` |
| `min_sqft` | int | Minimum square feet | `min_sqft=1000` |
| `max_sqft` | int | Maximum square feet | `max_sqft=3000` |
| `city` | string | City name (partial) | `city=nashville` |
| `zip_code` | string | ZIP code | `zip_code=37201` |
| `page` | int | Page number (search only) | `page=1` |
| `per_page` | int | Results per page (search only, max 100) | `per_page=20` |

### For `/api/metrics/fred`:

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `metric_name` | string | Metric identifier | `metric_name=median_price` |
| `series_id` | string | FRED series ID | `series_id=MEDLISPRIM31540` |
| `start_date` | string | Start date (YYYY-MM-DD) | `start_date=2023-01-01` |
| `end_date` | string | End date (YYYY-MM-DD) | `end_date=2024-12-31` |

## Available FRED Metrics

- `active_listings` - Active property listings count
- `median_price` - Median listing price
- `median_dom` - Median days on market
- `employment_non_farm` - Non-farm employment
- `msa_population` - MSA population
- `median_pp_sqft` - Median price per square foot
- `median_listing_price_change` - Median listing price change
- `msa_per_capita_income` - Per capita income

## Using with Python

```python
import requests

# Search properties
response = requests.get('http://127.0.0.1:5000/api/properties/search', params={
    'property_type': 'forsale',
    'min_price': 200000,
    'max_price': 400000,
    'min_beds': 3,
    'page': 1,
    'per_page': 20
})
data = response.json()
print(f"Found {data['pagination']['total_count']} properties")
for prop in data['properties']:
    print(f"{prop['address']}: ${prop['price']:,}")
```

## Using with JavaScript

```javascript
// Search properties
fetch('http://127.0.0.1:5000/api/properties/search?property_type=rental&min_beds=2&max_price=2000')
  .then(response => response.json())
  .then(data => {
    console.log(`Found ${data.pagination.total_count} rentals`);
    data.properties.forEach(prop => {
      console.log(`${prop.address}: $${prop.price}/mo`);
    });
  });

// Export to CSV
window.location.href = 'http://127.0.0.1:5000/api/properties/export?property_type=forsale&min_price=300000';
```

## Response Examples

### Search Response
```json
{
  "properties": [
    {
      "zpid": 123456789,
      "address": "123 Main St, Nashville, TN 37201",
      "price": 350000,
      "bedrooms": 3,
      "bathrooms": 2.0,
      "livingArea": 1800,
      "propertyType": "SINGLE_FAMILY",
      "latitude": 36.1627,
      "longitude": -86.7816,
      "imgSrc": "https://...",
      "detailUrl": "https://...",
      "daysOnZillow": 15,
      "listingStatus": "FOR_SALE"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total_count": 150,
    "total_pages": 8,
    "has_next": true,
    "has_prev": false
  }
}
```

### FRED Metrics Response
```json
{
  "metrics": [
    {
      "date": "2024-11-01",
      "metric_name": "median_price",
      "series_id": "MEDLISPRIM31540",
      "value": 425000.0
    }
  ],
  "count": 1
}
```

## Troubleshooting

**API returns empty results:**
- Make sure you've run `python app.py` to populate the database
- Check that the database file `BNASFR02.DB` exists

**Import errors when starting Flask:**
- Make sure you're running from the correct directory
- Check that `utils/__init__.py` exists

**Connection refused:**
- Verify Flask app is running on port 5000
- Check for port conflicts with other applications

**CSV export not downloading:**
- Use curl with `-o filename.csv` flag
- Or access the URL directly in a browser

## More Information

- Full API Documentation: `web/api/README.md`
- Implementation Details: `API_IMPLEMENTATION_SUMMARY.md`
- Run Tests: `python test_api.py`
- View Logs: `logs/api_YYYYMMDD.log`
