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
