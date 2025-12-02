#!/usr/bin/env python
"""
Backwards-compatible ETL runner

Usage: python run_etl.py
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from bna_market.services.etl_service import run_etl

if __name__ == "__main__":
    run_etl()
