"""
Nightly ETL refresh stub.

This script can be triggered by cron or a scheduler like Celery/Cloud
Tasks. It reuses the existing ETL orchestration entrypoint to keep
pipeline logic in one place.
"""

import logging
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from run_etl import run_etl  # noqa: E402

logger = logging.getLogger("cron_refresh")
logging.basicConfig(level=logging.INFO)


def refresh() -> None:
    logger.info("Starting nightly ETL refresh at %s", datetime.utcnow().isoformat())
    try:
        run_etl()
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.exception("Nightly ETL refresh failed: %s", exc)
        raise
    else:
        logger.info("Nightly ETL refresh completed successfully")


if __name__ == "__main__":
    refresh()
