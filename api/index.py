"""
Vercel serverless function entry point for BNA Market

This file is required by Vercel to serve the Flask application.
"""

import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

from bna_market.web.app import create_app

# Create Flask app
app = create_app()

# Vercel requires the app to be named 'app' or exposed as a handler
def handler(request, context):
    return app(request.environ, context)
