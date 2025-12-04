# Migration Guide: BNA Market v1.x to v2.0

This document outlines the changes from the flat directory structure (v1.x) to the refactored package structure (v2.0) with SaaS features.

## Major Changes

### 1. Package Structure
**Old (v1.x):**
```
bna-market/
├── app.py
├── pipelines/
│   ├── forSale.py
│   ├── rentalPipe.py
│   └── otherMetricsPipe.py
├── utils/
├── config/
└── web/
```

**New (v2.0):**
```
bna-market/
├── src/
│   └── bna_market/
│       ├── __init__.py
│       ├── __main__.py
│       ├── core/
│       │   └── config.py
│       ├── pipelines/
│       │   ├── for_sale.py
│       │   ├── rental.py
│       │   └── fred_metrics.py
│       ├── services/
│       │   └── etl_service.py
│       ├── utils/
│       └── web/
│           ├── app.py
│           ├── auth.py
│           ├── billing.py
│           └── api/
└── pyproject.toml
```

### 2. Configuration Consolidation

**Old:**
- Scattered configuration across multiple files
- Environment variables loaded in each module

**New:**
- Single `src/bna_market/core/config.py` file
- Centralized settings with `settings` dictionary
- Environment variable loading happens once
- Absolute database paths to avoid CWD issues

**Migration:**
```python
# Old
from config.settings import DATABASE_CONFIG
from pipelines.forSale import forSalePipe01

# New
from bna_market.core.config import DATABASE_CONFIG, settings
from bna_market.pipelines import fetch_for_sale_properties
```

### 3. Pipeline API Changes

**Old:**
```python
from pipelines.forSale import forSalePipe01
from pipelines.rentalPipe import rentalPipe01
from pipelines.otherMetricsPipe import fredMetricsPipe01

df_sales = forSalePipe01()
df_rentals = rentalPipe01()
df_fred = fredMetricsPipe01()
```

**New:**
```python
from bna_market.pipelines import (
    fetch_for_sale_properties,
    fetch_rental_properties,
    fetch_fred_metrics
)

df_sales = fetch_for_sale_properties()
df_rentals = fetch_rental_properties()
df_fred = fetch_fred_metrics()
```

### 4. ETL Service Refactor

**Old:**
```python
# Run app.py directly
python app.py
```

**New:**
```python
# Option 1: Use CLI
python -m bna_market etl run

# Option 2: Use service directly
from bna_market.services import ETLService
service = ETLService()
results = service.run_full_refresh()
```

### 5. Web Application

**Old:**
```python
# web/web_app.py
cd web
python web_app.py
```

**New:**
```python
# Application factory pattern
python -m bna_market web serve

# Or programmatically:
from bna_market.web.app import create_app
app = create_app()
app.run()
```

## New Features in v2.0

### 1. SaaS Features

**Authentication:**
```python
from bna_market.web.auth import auth_bp

# Endpoints:
# POST /auth/signup
# POST /auth/login
# GET  /auth/me
```

**Billing/Subscriptions:**
```python
from bna_market.web.billing import billing_bp

# Endpoints:
# POST /billing/webhook/stripe
# GET  /billing/plan
```

**API with Feature Gating:**
```python
from bna_market.web.api import api_bp
from bna_market.web.decorators import require_subscription

@require_subscription("properties_export")
def export_properties():
    # Feature requires active subscription
    pass
```

### 2. Environment Configuration

**New Environment Variables:**
```bash
# Required (same as v1.x)
RAPID_API_KEY=your-rapid-api-key
FRED_API_KEY=your-fred-api-key

# Optional (new in v2.0)
SECRET_KEY=your-flask-secret-key
DATABASE_PATH=BNASFR02.DB
ENABLE_AUTH_CHECKS=false
SUBSCRIPTION_CHECKS_ENABLED=false

# Stripe (optional)
STRIPE_API_KEY=sk_test_...
STRIPE_PRICE_ID=price_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

### 3. Enhanced Error Handling

- Retry logic with exponential backoff for API calls
- Data validation for Zillow and FRED responses
- Structured logging with file and console output
- Custom exception classes

### 4. CLI Commands

```bash
# Install package
pip install -e .

# Run ETL pipeline
bna-market etl run
# or
python -m bna_market etl run

# Start web server
bna-market web serve
# or
python -m bna_market web serve
```

## Migration Steps

### Step 1: Install Dependencies
```bash
# Install in editable mode
pip install -e .

# Or install with optional dependencies
pip install -e ".[production]"  # For production (includes gunicorn, stripe)
pip install -e ".[dev]"         # For development (includes pytest, black, etc.)
```

### Step 2: Update Environment Variables
Update your `.env` file with the new optional variables if needed.

### Step 3: Update Import Statements
Replace old imports with new package imports:

```python
# Old imports
from pipelines.forSale import forSalePipe01
from utils.database import get_db_connection
from config.settings import DATABASE_CONFIG

# New imports
from bna_market.pipelines import fetch_for_sale_properties
from bna_market.utils.database import get_db_connection
from bna_market.core.config import DATABASE_CONFIG
```

### Step 4: Update ETL Execution
```bash
# Old way (still works with deprecation warning)
python app.py

# New way
python -m bna_market etl run
```

### Step 5: Update Web Server Launch
```bash
# Old way
cd web && python web_app.py

# New way
python -m bna_market web serve
```

### Step 6: Test the Migration
```bash
# Test imports
python -c "from bna_market import __version__; print(__version__)"

# Test ETL (dry run - requires API keys)
python -m bna_market etl run

# Test web server
python -m bna_market web serve
```

## Backward Compatibility

The root `app.py` file has been updated to be a thin wrapper around the new package structure. It will work but displays deprecation warnings.

**Timeline:**
- v2.0 (current): Root `app.py` maintained with deprecation warnings
- v2.1 (future): Root `app.py` will be removed
- Old directory structure (`pipelines/`, `utils/`, `config/`) will be removed in v2.1

## Breaking Changes

1. **Pipeline function names** changed from `forSalePipe01()` to `fetch_for_sale_properties()`
2. **Import paths** changed from `pipelines.forSale` to `bna_market.pipelines`
3. **Configuration module** changed from `config.settings` to `bna_market.core.config`
4. **Web app** now uses application factory pattern instead of direct Flask instance

## Troubleshooting

### ImportError: No module named 'bna_market'
**Solution:** Install the package in editable mode:
```bash
pip install -e .
```

### Can't find database file
**Solution:** The new config uses absolute paths. Check `DATABASE_CONFIG["path"]`:
```python
from bna_market.core.config import DATABASE_CONFIG
print(DATABASE_CONFIG["path"])
```

### Authentication not working
**Solution:** Authentication is disabled by default. Enable it:
```bash
# In .env
ENABLE_AUTH_CHECKS=true
```

### API subscriptions not enforced
**Solution:** Subscription checks are disabled by default. Enable them:
```bash
# In .env
SUBSCRIPTION_CHECKS_ENABLED=true
```

## Support

For issues with migration, please:
1. Check the deprecation warnings in console output
2. Review this migration guide
3. Check `CLAUDE.md` for project overview
4. Open an issue on GitHub with your migration error
