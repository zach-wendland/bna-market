"""Vercel entrypoint for the BNA Market Flask application."""

import os
import sys

# Ensure the project src directory is on the path so the package can be imported
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "src"))

from bna_market.web.app import create_app


# Expose the Flask application directly. Vercel's Python runtime detects the
# WSGI app when the module-level variable is named ``app``; no custom handler
# function is needed and calling the app manually can lead to interface errors
# in the serverless environment.
app = create_app()
