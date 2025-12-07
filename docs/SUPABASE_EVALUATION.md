# Supabase vs SQLite Evaluation

## Current State: SQLite

The application currently uses SQLite (`BNASFR02.DB`) with three tables:
- `BNA_FORSALE` - For-sale property listings
- `BNA_RENTALS` - Rental property listings
- `BNA_FRED_METRICS` - Economic indicators from FRED

## Supabase: What It Provides

Supabase is a PostgreSQL-based backend-as-a-service with:
- Managed PostgreSQL database
- Real-time subscriptions
- Row-level security (RLS)
- Built-in authentication
- REST/GraphQL APIs (auto-generated)
- Edge functions

## Impact Analysis

### Positive Impacts

| Feature | Benefit | Effort |
|---------|---------|--------|
| **Scalability** | PostgreSQL handles concurrent connections; SQLite locks on writes | Low |
| **Real-time** | WebSocket updates when data changes (useful for live market data) | Medium |
| **Multi-user** | Concurrent ETL + web access without file locking | Low |
| **Vercel compatibility** | Serverless functions can't share SQLite files | Critical |
| **Free tier** | 500MB storage, 2GB bandwidth, 50K monthly requests | - |

### Negative Impacts

| Concern | Risk | Mitigation |
|---------|------|------------|
| **Data locality** | Latency for simple queries | Supabase edge (not available everywhere) |
| **Vendor lock-in** | PostgreSQL is standard, but Supabase APIs aren't | Use raw PostgreSQL client |
| **Cost at scale** | Beyond free tier: $25/mo Pro | Dataset is small (~10MB max) |
| **ETL complexity** | Need connection pooling for serverless | Use Supabase Python SDK |

## Migration Effort

### Code Changes Required

1. **Database utilities** (`bna_market/utils/database.py`)
   - Replace SQLite connection with `supabase-py` client
   - Change `read_table_safely` to use Supabase client

2. **ETL pipelines** (`bna_market/services/etl_service.py`)
   - Replace `df.to_sql()` with Supabase upserts
   - Handle connection pooling

3. **API routes** (`bna_market/web/api/routes.py`)
   - Replace raw SQL with Supabase query builder OR
   - Keep SQL with `psycopg2`/`asyncpg`

4. **Environment**
   - Add `SUPABASE_URL`, `SUPABASE_KEY`
   - Remove local DB path

### Estimated Changes
- ~200 lines of Python across 4-5 files
- New dependency: `supabase-py`
- Schema migration: Create tables via Supabase dashboard

## Recommendation

**Migrate to Supabase** for the following reasons:

1. **Vercel deployment is broken with SQLite** - Serverless can't persist files
2. **Free tier is sufficient** - Dataset is ~5MB, well under 500MB limit
3. **Real-time potential** - Could add live price updates
4. **Standard PostgreSQL** - Not locked in; can export/migrate easily

### Migration Path

1. Create Supabase project (free tier)
2. Create tables matching SQLite schema
3. Write Supabase adapter (swap SQLite functions)
4. Run ETL to populate Supabase
5. Update API routes
6. Remove SQLite dependency

### Alternative: Keep SQLite for Development

Use SQLite locally, Supabase in production:
```python
if os.getenv("SUPABASE_URL"):
    # Use Supabase in production
    db = SupabaseClient(...)
else:
    # Use SQLite locally
    db = sqlite3.connect(...)
```

This allows fast local development while supporting Vercel deployment.
