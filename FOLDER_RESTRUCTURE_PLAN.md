# Folder Structure Modernization Plan

## Current Structure Analysis

### **Current Layout** (❌ Issues Highlighted)

```
bna-market/
├── app.py                          # ❌ ETL orchestrator at root (should be in src/)
├── test_api.py                     # ❌ Manual test file at root (move to tests/)
├── BNASFR02.DB                     # ❌ Database at root (should be in data/)
├── .env                            # ✅ OK (gitignored)
├── requirements.txt                # ✅ OK
├── pytest.ini                      # ✅ OK
├── pyproject.toml                  # ✅ OK
│
├── config/                         # ✅ Good concept
│   ├── __init__.py
│   └── settings.py                 # ❌ But: Single config for all environments
│
├── pipelines/                      # ⚠️ OK but naming inconsistent
│   ├── __init__.py
│   ├── forSale.py                  # ❌ Inconsistent naming (camelCase)
│   ├── rentalPipe.py               # ❌ Inconsistent naming (Pipe suffix)
│   ├── otherMetricsPipe.py         # ❌ Inconsistent naming
│   └── zillow_base.py              # ✅ Good (snake_case)
│
├── utils/                          # ✅ Good
│   ├── __init__.py
│   ├── database.py
│   ├── env_validator.py
│   ├── exceptions.py
│   ├── logger.py
│   ├── retry.py
│   └── validators.py
│
├── scripts/                        # ✅ Good
│   ├── __init__.py
│   └── add_indexes.py
│
├── web/                            # ⚠️ Should be separate app
│   ├── web_app.py                  # ❌ Should be app.py or __init__.py
│   │
│   ├── api/                        # ✅ Good separation
│   │   ├── __init__.py
│   │   ├── routes.py               # ❌ All routes in one file (not scalable)
│   │   └── README.md
│   │
│   ├── utils/                      # ❌ Duplicate utils dir (confusing)
│   │   ├── __init__.py
│   │   ├── analytics.py            # ❌ Should be in services/
│   │   └── map_generator.py        # ❌ Should be in services/
│   │
│   ├── templates/                  # ✅ Good
│   │   ├── dashboard.html
│   │   ├── _rentals_table.html
│   │   └── _forsale_table.html
│   │
│   └── static/                     # ✅ Good
│       └── stylesheet.css
│
└── tests/                          # ✅ Good structure
    ├── __init__.py
    ├── conftest.py
    ├── fixtures/
    ├── unit/
    └── integration/
```

---

## Problems with Current Structure

### **Critical Issues:**

1. **No `src/` directory**
   - Application code mixed with config files at root
   - Hard to distinguish "code" from "project files"
   - Breaks Python packaging best practices

2. **No clear business logic layer**
   - ETL logic in `app.py` (orchestration) mixed with `pipelines/` (data fetching)
   - No `services/` or `domain/` layer
   - Hard to test business rules independently

3. **Inconsistent naming conventions**
   - `forSale.py` (camelCase) vs `zillow_base.py` (snake_case)
   - `rentalPipe.py` has "Pipe" suffix, `forSale.py` doesn't
   - Creates confusion about which files do what

4. **No models/schemas separation**
   - No SQLAlchemy models yet (planning for PostgreSQL migration)
   - No Pydantic schemas for API validation
   - Data structures implicit in DataFrames

5. **Web app structure not scalable**
   - All API routes in one 363-line file
   - `web/utils/` duplicates root `utils/` (confusing)
   - No blueprints organization (properties, metrics, auth)

6. **Missing directories:**
   - No `data/` for database files
   - No `migrations/` for Alembic (future)
   - No `docs/` for API documentation
   - No `scripts/deployment/` separation

---

## Proposed Modern Structure

### **Target Layout** (✅ Modern Best Practices)

```
bna-market/
│
├── .github/                        # 🆕 CI/CD workflows
│   └── workflows/
│       ├── ci.yml                  # Test + lint on every PR
│       ├── cd.yml                  # Deploy on main merge
│       └── security.yml            # Dependency scanning
│
├── docs/                           # 🆕 Documentation
│   ├── api/                        # API documentation
│   │   └── openapi.yaml            # OpenAPI 3.0 spec
│   ├── architecture.md             # System design
│   ├── deployment.md               # Deployment guide
│   └── contributing.md             # Dev guidelines
│
├── src/                            # 🆕 All application code here
│   └── bna_market/                 # 🆕 Proper Python package
│       │
│       ├── __init__.py             # Package metadata
│       ├── __main__.py             # Entry point: python -m bna_market
│       │
│       ├── cli/                    # 🆕 CLI commands
│       │   ├── __init__.py
│       │   ├── etl.py              # ETL commands (run, backfill)
│       │   └── db.py               # DB commands (migrate, seed)
│       │
│       ├── core/                   # 🆕 Business logic
│       │   ├── __init__.py
│       │   ├── config.py           # Config management
│       │   ├── constants.py        # App constants
│       │   ├── exceptions.py       # Custom exceptions
│       │   └── dependencies.py     # Dependency injection
│       │
│       ├── models/                 # 🆕 Data models
│       │   ├── __init__.py
│       │   ├── database.py         # SQLAlchemy Base
│       │   ├── property.py         # Property models
│       │   ├── metrics.py          # FRED metrics models
│       │   └── schemas.py          # Pydantic schemas
│       │
│       ├── pipelines/              # ♻️ Refactored
│       │   ├── __init__.py
│       │   ├── base.py             # Base pipeline class
│       │   ├── zillow.py           # 🔄 Renamed from zillow_base
│       │   ├── for_sale.py         # 🔄 Renamed from forSale
│       │   ├── rentals.py          # 🔄 Renamed from rentalPipe
│       │   └── fred_metrics.py     # 🔄 Renamed from otherMetricsPipe
│       │
│       ├── services/               # 🆕 Business logic layer
│       │   ├── __init__.py
│       │   ├── etl_service.py      # ETL orchestration (from app.py)
│       │   ├── property_service.py # Property CRUD operations
│       │   ├── metrics_service.py  # Metrics aggregation
│       │   ├── analytics.py        # 🔄 Moved from web/utils
│       │   └── map_generator.py    # 🔄 Moved from web/utils
│       │
│       ├── repositories/           # 🆕 Data access layer
│       │   ├── __init__.py
│       │   ├── base.py             # Base repository pattern
│       │   ├── property_repo.py    # Property data access
│       │   └── metrics_repo.py     # Metrics data access
│       │
│       ├── utils/                  # ♻️ Consolidated utilities
│       │   ├── __init__.py
│       │   ├── database.py         # DB connection management
│       │   ├── logger.py           # Logging setup
│       │   ├── retry.py            # Retry decorator
│       │   ├── validators.py       # Data validation
│       │   └── env.py              # 🔄 Renamed from env_validator
│       │
│       └── web/                    # ♻️ Refactored Flask app
│           ├── __init__.py         # Flask app factory
│           ├── app.py              # 🔄 Renamed from web_app.py
│           │
│           ├── api/                # REST API (versioned)
│           │   ├── __init__.py
│           │   ├── deps.py         # API dependencies
│           │   │
│           │   └── v1/             # 🆕 API versioning
│           │       ├── __init__.py
│           │       ├── properties.py   # 🔄 Split from routes.py
│           │       ├── metrics.py      # 🔄 Split from routes.py
│           │       └── health.py       # 🔄 Split from routes.py
│           │
│           ├── templates/          # Same, but add components/
│           │   ├── base.html       # 🆕 Base template
│           │   ├── dashboard.html
│           │   │
│           │   └── components/     # 🆕 Reusable components
│           │       ├── _pagination.html
│           │       ├── _filter_form.html
│           │       ├── _property_table.html
│           │       └── _loading.html
│           │
│           ├── static/
│           │   ├── css/            # 🆕 Organized CSS
│           │   │   ├── main.css
│           │   │   └── components.css
│           │   │
│           │   ├── js/             # 🆕 Organized JS
│           │   │   ├── dashboard.js
│           │   │   ├── filters.js
│           │   │   └── utils.js
│           │   │
│           │   └── icons/          # 🆕 PWA icons
│           │       ├── favicon.ico
│           │       ├── icon-192.png
│           │       └── icon-512.png
│           │
│           └── middleware/         # 🆕 Flask middleware
│               ├── __init__.py
│               ├── auth.py         # Future: Authentication
│               ├── logging.py      # Request logging
│               └── error_handler.py # Error handling
│
├── tests/                          # ♻️ Enhanced test structure
│   ├── __init__.py
│   ├── conftest.py
│   │
│   ├── unit/                       # Unit tests mirror src/ structure
│   │   ├── core/
│   │   ├── models/
│   │   ├── pipelines/
│   │   ├── services/
│   │   ├── repositories/
│   │   └── utils/
│   │
│   ├── integration/                # Integration tests
│   │   ├── test_etl_workflow.py
│   │   ├── test_api_endpoints.py
│   │   └── test_database.py
│   │
│   ├── e2e/                        # 🆕 End-to-end tests
│   │   └── test_dashboard.py
│   │
│   └── fixtures/                   # Test data
│       ├── __init__.py
│       ├── properties.py
│       └── metrics.py
│
├── migrations/                     # 🆕 Alembic migrations
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       └── 001_initial_schema.py
│
├── scripts/                        # ♻️ Reorganized scripts
│   ├── __init__.py
│   ├── development/                # 🆕 Dev scripts
│   │   ├── seed_db.py
│   │   └── reset_db.py
│   │
│   ├── deployment/                 # 🆕 Deploy scripts
│   │   ├── migrate.sh
│   │   └── health_check.sh
│   │
│   └── maintenance/                # 🆕 Maintenance
│       ├── backup_db.py
│       └── cleanup_logs.py
│
├── data/                           # 🆕 Data files
│   ├── .gitkeep
│   ├── BNASFR02.DB                 # 🔄 Moved from root
│   └── backups/
│
├── config/                         # ♻️ Enhanced config
│   ├── __init__.py
│   ├── base.py                     # 🆕 Base config
│   ├── development.py              # 🆕 Dev settings
│   ├── staging.py                  # 🆕 Staging settings
│   ├── production.py               # 🆕 Prod settings
│   └── testing.py                  # 🆕 Test settings
│
├── docker/                         # 🆕 Docker configs
│   ├── Dockerfile
│   ├── Dockerfile.dev
│   ├── docker-compose.yml
│   └── nginx.conf
│
├── .env.example                    # ✅ Keep
├── .gitignore                      # ✅ Keep
├── .editorconfig                   # ✅ Keep
├── .pre-commit-config.yaml         # ✅ Keep
├── pytest.ini                      # ✅ Keep (or move to pyproject.toml)
├── pyproject.toml                  # ✅ Keep (enhanced)
├── requirements.txt                # ♻️ Split into:
├── requirements-base.txt           # 🆕 Core dependencies
├── requirements-dev.txt            # ✅ Already exists
├── requirements-prod.txt           # 🆕 Production extras
│
├── README.md                       # ✅ Keep
├── CONTRIBUTING.md                 # 🆕 Dev guidelines
├── CHANGELOG.md                    # 🆕 Version history
├── LICENSE                         # 🆕 License file
│
└── Makefile                        # 🆕 Common commands
```

---

## Key Architectural Changes

### **1. Layered Architecture** (NEW)

```
┌─────────────────────────────────────────┐
│         Presentation Layer              │
│  (web/templates, web/static, web/api)   │
└─────────────────────┬───────────────────┘
                      │
┌─────────────────────▼───────────────────┐
│         Service Layer                   │
│  (services/* - business logic)          │
└─────────────────────┬───────────────────┘
                      │
┌─────────────────────▼───────────────────┐
│      Repository Layer                   │
│  (repositories/* - data access)         │
└─────────────────────┬───────────────────┘
                      │
┌─────────────────────▼───────────────────┐
│         Data Layer                      │
│  (models/* - ORM, schemas)              │
└─────────────────────────────────────────┘
```

### **2. Dependency Flow**

```
pipelines/        →  services/        →  repositories/  →  models/
(data fetch)          (orchestration)     (data access)     (schema)
                              ↓
                          web/api/
                          (HTTP)
```

### **3. Configuration Hierarchy**

```
config/base.py          ← Base settings (all environments)
    ├── development.py  ← Dev overrides (debug=True, local DB)
    ├── staging.py      ← Staging overrides
    ├── production.py   ← Prod overrides (debug=False, PG, logging)
    └── testing.py      ← Test overrides (temp DB, mocks)
```

---

## Migration Plan (4 Phases)

### **Phase 1: Foundation** (2-3 hours)
*Set up new structure without breaking existing code*

1. Create `src/bna_market/` directory
2. Move all existing code into `src/bna_market/` preserving structure
3. Update imports (add `from bna_market.` prefix)
4. Test that everything still works
5. Create `__init__.py` files for all packages
6. Update `pyproject.toml` with package metadata

**Risk**: Low (just moving files, not changing logic)

### **Phase 2: Reorganization** (3-4 hours)
*Rename and restructure without changing code logic*

1. Rename pipeline files (forSale → for_sale, etc.)
2. Split `web/api/routes.py` into versioned modules
3. Create `services/` layer, move ETL logic from `app.py`
4. Consolidate utils (merge `web/utils/` into root `utils/`)
5. Move `BNASFR02.DB` to `data/`
6. Update all imports
7. Run tests to verify

**Risk**: Medium (lots of import changes, but tests catch issues)

### **Phase 3: New Layers** (4-6 hours)
*Add new architectural layers*

1. Create `models/` with SQLAlchemy models
2. Create `repositories/` for data access
3. Create `services/` for business logic
4. Refactor existing code to use new layers
5. Update tests to match new structure
6. Add Alembic migrations setup

**Risk**: Medium-High (architectural changes, requires careful testing)

### **Phase 4: Enhancement** (3-4 hours)
*Add new features and polish*

1. Create config hierarchy (dev/staging/prod)
2. Add CLI commands (`cli/`)
3. Add middleware layer
4. Split requirements files
5. Create Makefile for common tasks
6. Add Docker setup
7. Enhance documentation

**Risk**: Low (additive changes, existing code still works)

---

## File-by-File Migration Map

### **Root Level**
```
app.py                    →  src/bna_market/services/etl_service.py
test_api.py               →  tests/integration/test_api_manual.py (or DELETE)
BNASFR02.DB               →  data/BNASFR02.DB
```

### **Pipelines**
```
pipelines/forSale.py           →  src/bna_market/pipelines/for_sale.py
pipelines/rentalPipe.py        →  src/bna_market/pipelines/rentals.py
pipelines/otherMetricsPipe.py  →  src/bna_market/pipelines/fred_metrics.py
pipelines/zillow_base.py       →  src/bna_market/pipelines/zillow.py
```

### **Utils** (Consolidate)
```
utils/database.py         →  src/bna_market/utils/database.py
utils/logger.py           →  src/bna_market/utils/logger.py
utils/validators.py       →  src/bna_market/utils/validators.py
utils/retry.py            →  src/bna_market/utils/retry.py
utils/env_validator.py    →  src/bna_market/utils/env.py
utils/exceptions.py       →  src/bna_market/core/exceptions.py

web/utils/analytics.py    →  src/bna_market/services/analytics.py
web/utils/map_generator.py →  src/bna_market/services/map_generator.py
```

### **Web App**
```
web/web_app.py            →  src/bna_market/web/app.py
web/api/routes.py         →  Split into:
                              ├── src/bna_market/web/api/v1/properties.py
                              ├── src/bna_market/web/api/v1/metrics.py
                              └── src/bna_market/web/api/v1/health.py

web/templates/            →  src/bna_market/web/templates/
web/static/               →  src/bna_market/web/static/
```

### **Config**
```
config/settings.py        →  Split into:
                              ├── config/base.py
                              ├── config/development.py
                              ├── config/production.py
                              └── config/testing.py
```

---

## Import Changes Example

### **Before:**
```python
# app.py
from pipelines.forSale import forSalePipe01
from utils.logger import setup_logger
from utils.database import get_db_connection
```

### **After:**
```python
# src/bna_market/services/etl_service.py
from bna_market.pipelines.for_sale import fetch_for_sale_properties
from bna_market.utils.logger import setup_logger
from bna_market.repositories.property_repo import PropertyRepository
```

---

## Benefits of New Structure

### **Development**
✅ Clear separation of concerns (easier to understand)
✅ Consistent naming (snake_case everywhere)
✅ Easier to find files (logical organization)
✅ Better IDE navigation (proper package structure)
✅ Scalable (add features without mess)

### **Testing**
✅ Test structure mirrors code (easy to find corresponding tests)
✅ Repository pattern makes mocking easier
✅ Service layer can be tested without web framework

### **Deployment**
✅ Proper Python package (can `pip install -e .`)
✅ Clear separation of dev/prod configs
✅ Docker-ready structure
✅ Migrations versioned in code

### **Collaboration**
✅ Industry-standard structure (new devs know where to look)
✅ Clear contribution guidelines
✅ API versioning ready for breaking changes
✅ Better documentation organization

---

## Makefile Commands (NEW)

```makefile
# Development
make install          # Install dependencies
make dev              # Run dev server with auto-reload
make shell            # Open Python shell with app context
make lint             # Run black + flake8 + mypy
make format           # Auto-format with black
make test             # Run full test suite
make test-unit        # Run unit tests only
make test-cov         # Run tests with coverage report

# Database
make db-migrate       # Create new migration
make db-upgrade       # Apply migrations
make db-downgrade     # Rollback migration
make db-seed          # Seed database with sample data
make db-reset         # Drop + recreate + seed

# ETL
make etl-run          # Run full ETL pipeline
make etl-backfill     # Backfill historical data

# Docker
make docker-build     # Build Docker image
make docker-up        # Start all services
make docker-down      # Stop all services
make docker-logs      # View logs

# Deployment
make deploy-staging   # Deploy to staging
make deploy-prod      # Deploy to production
```

---

## Timeline & Effort

| Phase | Hours | Can Break Things? | Priority |
|-------|-------|-------------------|----------|
| Phase 1: Foundation | 2-3 | Low risk | **Do First** |
| Phase 2: Reorganization | 3-4 | Medium risk | **Do Second** |
| Phase 3: New Layers | 4-6 | Medium-high risk | **Do Third** |
| Phase 4: Enhancement | 3-4 | Low risk | **Do Last** |
| **Total** | **12-17 hours** | - | - |

---

## Rollout Strategy

### **Option A: Big Bang** (2-3 days, risky)
- Do all phases at once
- Massive refactor
- High risk of breaking things
- **NOT RECOMMENDED**

### **Option B: Incremental** (1-2 weeks, safe) ✅ **RECOMMENDED**
- Phase 1 → commit → test → deploy
- Phase 2 → commit → test → deploy
- Phase 3 → commit → test → deploy
- Phase 4 → commit → test → deploy
- Lower risk, easier to debug

### **Option C: Parallel Branch** (flexible)
- Create `refactor/folder-structure` branch
- Complete all phases
- Extensive testing before merge
- **Good for production systems**

---

## Next Steps

**I can start with Phase 1 now (2-3 hours):**
1. Create `src/bna_market/` structure
2. Move all existing code (no logic changes)
3. Update imports
4. Verify tests pass
5. Commit as "Restructure: Move code to src/ package"

**Want me to proceed?** Or would you prefer to review the plan first?
