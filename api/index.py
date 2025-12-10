"""Vercel entrypoint for the BNA Market Flask application."""

from bna_market.web.app import create_app

# Force Vercel to reload this module by adding timestamp
# Last updated: 2025-12-10 14:47 UTC
# This file MUST be modified to trigger Vercel Python function reload

# Expose the Flask application directly. Vercel's Python runtime detects the
# WSGI app when the module-level variable is named ``app``; no custom handler
# function is needed and calling the app manually can lead to interface errors
# in the serverless environment.
app = create_app()

# Verify app loaded with all blueprints
print(f"[Vercel] Flask app created with {len(app.url_map._rules)} routes")
print(f"[Vercel] Registered blueprints: {list(app.blueprints.keys())}")
