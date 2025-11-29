# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

BNA Market is a Nashville real estate market analytics application that collects property listings from Zillow and economic indicators from FRED, stores them in SQLite, and visualizes them in a Flask dashboard with Plotly charts.

**Geographic Focus**: Nashville, TN metropolitan area (polygon: -87.2316 36.5227 to -86.3316 35.8027)

## Architecture

### Data Flow
1. **Data Collection** (`pipelines/`) → Fetch data from external APIs
2. **Data Storage** (`app.py`) → Transform and load into SQLite database
3. **Data Visualization** (`web/web_app.py`) → Flask dashboard with Plotly charts

### Database Schema (BNASFR02.DB)
- `BNA_FORSALE` - For-sale property listings from Zillow (unique on `zpid`)
- `BNA_RENTALS` - Rental property listings from Zillow (unique on `zpid`)
- `BNA_FRED_METRICS` - Economic indicators from FRED (unique on `date` + `series_id`)

### Pipeline Architecture

**pipelines/forSale.py** - Zillow for-sale properties
- Fetches up to 20 pages of listings
- Filters: $100k-$700k, 1-5 beds, 1-4 baths, 700-5000 sqft, built after 1990
- Returns: Raw DataFrame with nested JSON fields

**pipelines/rentalPipe.py** - Zillow rental properties
- Fetches up to 20 pages of listings
- Filters: $1400-$3200/month, 1-4 beds, 1-4 baths, 550-6000 sqft, built after 1979
- Parses and explodes `units` array for multi-unit properties
- Returns: Flattened DataFrame with `_unit` suffix columns

**pipelines/otherMetricsPipe.py** - FRED economic indicators
- Fetches 15 years of historical data for 8 Nashville MSA metrics:
  - `active_listings`, `median_price`, `median_dom` (days on market)
  - `employment_non_farm`, `msa_population`, `median_pp_sqft`
  - `median_listing_price_change`, `msa_per_capita_income`
- Returns: Long-format DataFrame with columns: `date`, `metric_name`, `series_id`, `value`

### ETL Update Strategy (app.py)

All three update functions (`updateSalesTable`, `updateRentalsTable`, `updateFredMetricsTable`):
1. Call pipeline function to fetch new data
2. Skip update if DataFrame is empty
3. Read existing table data
4. Merge new data with existing (deduplication based on unique keys)
5. Replace entire table with merged dataset

**Important**: Dict/list columns are JSON-serialized before SQLite storage.

## Development Commands

### Run ETL Pipeline
```bash
python app.py
```
Updates all three database tables (rentals, sales, FRED metrics).

### Run Web Dashboard
```bash
cd web
python web_app.py
```
Launches Flask app at http://127.0.0.1:5000 (default port).

**Note**: Dashboard will show "no data available" messages until `python app.py` has been run at least once to populate the database.

### Test Individual Pipelines
```bash
# Test for-sale pipeline (has print statement at end)
python pipelines/forSale.py

# Test rental pipeline
python -c "from pipelines.rentalPipe import rentalPipe01; print(rentalPipe01())"

# Test FRED metrics pipeline
python -c "from pipelines.otherMetricsPipe import fredMetricsPipe01; print(fredMetricsPipe01())"
```

## Environment Setup

### Required Environment Variables (.env)
```
RAPID_API_KEY=<your-rapidapi-key>  # For Zillow API access
FRED_API_KEY=<your-fred-api-key>   # For FRED economic data
```

### Expected Dependencies
Based on imports across the codebase:
- requests
- pandas
- plotly
- flask
- fredapi
- python-dotenv
- sqlite3 (standard library)

**Note**: No `requirements.txt` exists yet. Create one if adding dependencies.

## Code Organization Notes

### Completed
- `pipelines/` - All three data collection pipelines are functional
- `app.py` - ETL orchestration with deduplication logic
- `web/web_app.py` - Dashboard with 4 FRED time-series charts + 2 property histograms

### Incomplete
- `utils/etlRentals.py` - Marked "NOT FINISHED YET", contains experimental rental data cleaning logic (not used in main pipeline)
- `etl/` - Empty directory

### Web Application Structure
- `web/templates/dashboard.html` - Main dashboard template
- `web/templates/_rentals_table.html` - Rental property table partial
- `web/templates/_forsale_table.html` - For-sale property table partial
- `web/static/stylesheet.css` - Dashboard styling

## API Rate Limits & Pagination

**Zillow API** (via RapidAPI):
- Both pipelines fetch maximum 20 pages
- 0.5 second delay between page requests
- Error handling: breaks loop on RequestException, JSONDecodeError, or any unexpected error

**FRED API**:
- No explicit rate limiting implemented
- Fetches 15 years of data in single request per series
- 8 series total, fetched sequentially

## Common Gotchas

1. **Duplicate `load_dotenv()`**: `rentalPipe.py` calls `load_dotenv()` twice (lines 10-11)
2. **Print statement in production**: `forSale.py` has `print(forSalePipe01())` at line 75 - runs every import
3. **Relative DB path**: `web/web_app.py` uses `"../BNASFR02.DB"` - only works when running from `web/` directory
4. **No data validation**: Pipelines return empty DataFrames on API failures without raising exceptions
5. **Replace vs Append**: All update functions use `if_exists='replace'` - entire table is rewritten on every update (mitigated by merge logic)
