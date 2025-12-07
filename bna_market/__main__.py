"""
CLI entry point for BNA Market application

Usage:
    python -m bna_market etl run        # Run ETL pipeline
    python -m bna_market web serve      # Start web server
    python -m bna_market db migrate     # Run migrations
"""

import os
import sys
import argparse
from bna_market.services.etl_service import run_etl
from bna_market.web.app import create_app


def main():
    parser = argparse.ArgumentParser(description="BNA Market CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # ETL commands
    etl_parser = subparsers.add_parser("etl", help="ETL operations")
    etl_subparsers = etl_parser.add_subparsers(dest="etl_command")
    etl_subparsers.add_parser("run", help="Run full ETL pipeline")

    # Web commands
    web_parser = subparsers.add_parser("web", help="Web server operations")
    web_subparsers = web_parser.add_subparsers(dest="web_command")
    web_subparsers.add_parser("serve", help="Start Flask development server")

    args = parser.parse_args()

    if args.command == "etl" and args.etl_command == "run":
        print("Running ETL pipeline...")
        run_etl()
    elif args.command == "web" and args.web_command == "serve":
        print("Starting web server...")
        app = create_app()
        # Use environment variable for debug mode instead of hardcoding
        debug_mode = os.getenv("FLASK_DEBUG", "true").lower() in ("true", "1", "yes")
        app.run(debug=debug_mode, host="0.0.0.0", port=5000)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
