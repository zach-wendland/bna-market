# BNA Market API Documentation

REST API endpoints for querying Nashville real estate data and economic metrics.

## Base URL
```
http://127.0.0.1:5000/api
```

## Endpoints

### 1. Search Properties
Search and filter property listings with pagination.

**Endpoint:** `GET /api/properties/search`

**Required Parameters:**
- `property_type` (string): Either `forsale` or `rental`

**Optional Parameters:**
- `min_price` (float): Minimum price
- `max_price` (float): Maximum price
- `min_beds` (int): Minimum bedrooms
- `max_beds` (int): Maximum bedrooms
- `min_baths` (float): Minimum bathrooms
- `max_baths` (float): Maximum bathrooms
- `min_sqft` (int): Minimum square footage
- `max_sqft` (int): Maximum square footage
- `city` (string): City name (partial match, case-insensitive)
- `zip_code` (string): ZIP code (exact match)
- `page` (int): Page number (default: 1)
- `per_page` (int): Items per page (default: 20, max: 100)

**Example Request:**
```bash
curl "http://127.0.0.1:5000/api/properties/search?property_type=forsale&min_price=200000&max_price=400000&min_beds=2&city=nashville&page=1&per_page=20"
```

**Example Response:**
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

---

### 2. Export Properties to CSV
Export filtered properties as a downloadable CSV file.

**Endpoint:** `GET /api/properties/export`

**Parameters:** Same as `/api/properties/search` (excluding pagination parameters)

**Example Request:**
```bash
curl "http://127.0.0.1:5000/api/properties/export?property_type=rental&min_price=1500&max_price=2500&min_beds=2" -o properties.csv
```

**Response:** CSV file download with columns:
- zpid
- address
- price
- bedrooms
- bathrooms
- livingArea
- propertyType
- latitude
- longitude
- daysOnZillow
- listingStatus
- detailUrl

---

### 3. Get FRED Economic Metrics
Retrieve economic indicators from the FRED database.

**Endpoint:** `GET /api/metrics/fred`

**Optional Parameters:**
- `metric_name` (string): Filter by metric name (e.g., `median_price`, `active_listings`)
- `series_id` (string): Filter by FRED series ID
- `start_date` (string): Start date in YYYY-MM-DD format
- `end_date` (string): End date in YYYY-MM-DD format

**Available Metrics:**
- `active_listings` - Active property listings count
- `median_price` - Median listing price
- `median_dom` - Median days on market
- `employment_non_farm` - Non-farm employment (thousands)
- `msa_population` - MSA population
- `median_pp_sqft` - Median price per square foot
- `median_listing_price_change` - Median listing price change
- `msa_per_capita_income` - Per capita income

**Example Request:**
```bash
curl "http://127.0.0.1:5000/api/metrics/fred?metric_name=median_price&start_date=2023-01-01&end_date=2024-12-31"
```

**Example Response:**
```json
{
  "metrics": [
    {
      "date": "2024-11-01",
      "metric_name": "median_price",
      "series_id": "MEDLISPRIM31540",
      "value": 425000.0
    },
    {
      "date": "2024-10-01",
      "metric_name": "median_price",
      "series_id": "MEDLISPRIM31540",
      "value": 420000.0
    }
  ],
  "count": 2
}
```

---

### 4. Health Check
Verify API status and available endpoints.

**Endpoint:** `GET /api/health`

**Example Request:**
```bash
curl "http://127.0.0.1:5000/api/health"
```

**Example Response:**
```json
{
  "status": "healthy",
  "api_version": "1.0",
  "endpoints": [
    "/api/properties/search",
    "/api/properties/export",
    "/api/metrics/fred",
    "/api/health"
  ]
}
```

---

## Error Responses

All endpoints return standard HTTP status codes and JSON error messages:

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

---

## Usage Examples

### JavaScript (Fetch API)
```javascript
// Search for rental properties
fetch('http://127.0.0.1:5000/api/properties/search?property_type=rental&min_beds=2&max_price=2000')
  .then(response => response.json())
  .then(data => console.log(data.properties));

// Export to CSV
window.location.href = 'http://127.0.0.1:5000/api/properties/export?property_type=forsale&min_price=300000';

// Get FRED metrics
fetch('http://127.0.0.1:5000/api/metrics/fred?metric_name=active_listings')
  .then(response => response.json())
  .then(data => console.log(data.metrics));
```

### Python (requests)
```python
import requests

# Search properties
response = requests.get('http://127.0.0.1:5000/api/properties/search', params={
    'property_type': 'forsale',
    'min_price': 200000,
    'max_price': 500000,
    'min_beds': 3,
    'page': 1,
    'per_page': 50
})
properties = response.json()['properties']

# Export to CSV
response = requests.get('http://127.0.0.1:5000/api/properties/export', params={
    'property_type': 'rental',
    'min_beds': 2
})
with open('rentals.csv', 'wb') as f:
    f.write(response.content)

# Get FRED metrics
response = requests.get('http://127.0.0.1:5000/api/metrics/fred', params={
    'metric_name': 'median_price',
    'start_date': '2023-01-01'
})
metrics = response.json()['metrics']
```

---

## Notes

- All monetary values are in USD
- Square footage is in square feet
- Dates follow ISO 8601 format (YYYY-MM-DD)
- Property search results are ordered by price (descending)
- FRED metrics are ordered by date (descending), then metric name
- Pagination uses 1-based indexing
- Maximum items per page is capped at 100
