"""
Environment validation for BNA Market application

Validates required environment variables are set before running pipelines.
"""

import os
from typing import Dict
from dotenv import load_dotenv
from bna_market.utils.logger import setup_logger

logger = setup_logger("env_validator")


def validate_environment(reload_dotenv: bool = True) -> bool:
    """
    Validate all required environment variables are set

    Args:
        reload_dotenv: Whether to reload .env file (default True)
                      Set to False in tests to check actual env vars

    Returns:
        True if all required variables are present, False otherwise
    """
    if reload_dotenv:
        load_dotenv()

    required_vars: Dict[str, str] = {
        "RAPID_API_KEY": "RapidAPI key for Zillow data",
        "FRED_API_KEY": "FRED API key for economic indicators",
    }

    missing_vars = []

    for var_name, description in required_vars.items():
        value = os.getenv(var_name)
        if not value:
            missing_vars.append(f"{var_name} ({description})")
            logger.error(f"Missing required environment variable: {var_name}")
        else:
            logger.info(f"[OK] {var_name} is set")

    if missing_vars:
        logger.error(f"Missing {len(missing_vars)} required environment variables:")
        for var in missing_vars:
            logger.error(f"  - {var}")
        logger.error("Please check your .env file")
        return False

    logger.info("All required environment variables are set")
    return True
