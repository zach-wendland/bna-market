"""
DEPRECATED: Legacy entry point for backward compatibility

This file is maintained for backward compatibility with the old flat structure.
New deployments should use the refactored package structure:

    python -m bna_market etl run        # Run ETL pipeline
    python -m bna_market web serve      # Start web server

Or use the CLI command after installation:

    pip install -e .
    bna-market etl run                  # Run ETL pipeline
    bna-market web serve                # Start web server

This wrapper will be removed in a future version.
"""

import warnings

warnings.warn(
    "app.py is deprecated. Use 'python -m bna_market etl run' instead.",
    DeprecationWarning,
    stacklevel=2
)

from bna_market.services.etl_service import run_etl

if __name__ == "__main__":
    print("=" * 70)
    print("DEPRECATION WARNING: app.py is deprecated")
    print("Use 'python -m bna_market etl run' or 'bna-market etl run' instead")
    print("=" * 70)
    print()

    run_etl()
