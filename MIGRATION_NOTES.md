# Migration from Vercel to Railway/Render

## Summary

This repository has been configured for deployment on Railway or Render instead of Vercel due to bundle size limitations.

## What Changed

### ✅ Added Files
- `Procfile` - Process definition for Railway/Render
- `runtime.txt` - Python version specification
- `render.yaml` - Render-specific configuration
- `railway.json` - Railway-specific configuration
- `DEPLOYMENT.md` - Comprehensive deployment guide
- `.slugignore` - Exclude unnecessary files from deployment
- `.env.production.example` - Production environment template
- `test_deployment.sh` - Deployment readiness checker

### 📝 Modified Files
- `requirements.txt` - Added `gunicorn==21.2.0` for production server
- `src/bna_market/web/app.py` - Enhanced database path configuration with environment variable support

### 🗑️ Deprecated Files (Can Be Removed)

**Vercel-specific** (no longer needed):
- `vercel.json` - Vercel configuration
- `api/index.py` - Vercel serverless function entrypoint

**Optional cleanup**:
- `test_api.py` - Manual API testing file (replaced by proper test suite in `tests/`)
- `web/web_app.py` - Legacy Flask app (replaced by `src/bna_market/web/app.py` factory pattern)

## Why We Migrated

Vercel has a hard limit of **250 MB** (uncompressed) for serverless functions, inherited from AWS Lambda. Our application requires:

- pandas: ~70 MB
- plotly: ~144 MB
- numpy: ~60 MB
- **Total: ~274 MB** ❌

This exceeds Vercel's limit, making deployment impossible without major architectural changes.

Railway and Render don't have these bundle size restrictions, making them better suited for data-heavy Python applications.

## Cleanup Commands (Optional)

If you want to completely remove Vercel artifacts:

```bash
# Remove Vercel-specific files
rm vercel.json
rm -rf api/
rm test_api.py

# Remove legacy web app (if using new src/ structure)
rm -rf web/

# Commit cleanup
git add .
git commit -m "Remove Vercel artifacts and legacy files"
git push origin main
```

**⚠️ Warning**: Only remove `web/` directory if you've confirmed all functionality has been migrated to `src/bna_market/web/`.

## Next Steps

1. Review `DEPLOYMENT.md` for deployment instructions
2. Choose Railway or Render as your hosting platform
3. Set up environment variables in your chosen platform
4. Deploy and populate database with initial data

## Rollback Plan

If you need to revert to Vercel (e.g., for a different project):

1. The Vercel files are still in the repository
2. They're just not being used by Railway/Render
3. You can use both platforms simultaneously (API on one, web on another)

## Questions?

- Railway issues: See `DEPLOYMENT.md` or [docs.railway.app](https://docs.railway.app)
- Render issues: See `DEPLOYMENT.md` or [render.com/docs](https://render.com/docs)
