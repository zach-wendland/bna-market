#!/usr/bin/env python
"""
Backwards-compatible ETL runner

Usage: python run_etl.py
"""

from bna_market.services.etl_service import run_etl

if __name__ == "__main__":
    run_etl()
