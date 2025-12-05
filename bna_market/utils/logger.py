"""
Logging infrastructure for BNA Market application

Provides structured logging with timestamps, log levels, and both console and file output.
"""

import logging
import sys
import os
from datetime import datetime
from typing import Optional


def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Configure structured logging with timestamps

    Args:
        name: Logger name (typically module name)
        level: Logging level (default: INFO)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Prevent duplicate handlers if logger already exists
    if logger.handlers:
        return logger

    # Console handler for stdout (always enabled)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)

    # Formatter with timestamp, logger name, level, and message
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (optional - fails gracefully in serverless environments)
    try:
        # Try current directory first, fallback to /tmp for serverless
        log_dir = "logs"
        if not os.access(".", os.W_OK):
            # Read-only filesystem (serverless), use /tmp
            log_dir = "/tmp/logs"

        if not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)

        log_file = os.path.join(log_dir, f'{name}_{datetime.now().strftime("%Y%m%d")}.log')
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)  # File gets all debug messages
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except (OSError, PermissionError) as e:
        # File logging not available (serverless/read-only filesystem)
        # Console logging will still work
        logger.debug(f"File logging disabled: {e}")

    return logger
