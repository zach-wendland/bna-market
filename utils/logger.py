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

    # Console handler for stdout
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)

    # File handler (create logs directory if it doesn't exist)
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_file = os.path.join(log_dir, f'{name}_{datetime.now().strftime("%Y%m%d")}.log')
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)  # File gets all debug messages

    # Formatter with timestamp, logger name, level, and message
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger
