#!/usr/bin/env python
"""
Backwards-compatible web server runner

Usage: python run_web.py
"""

from bna_market.web.app import create_app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=5000)
