"""
Environment validation for BNA Market application

Validates required environment variables are set before running pipelines.
"""
import os
from typing import Dict
from dotenv import load_dotenv
from utils.logger import setup_logger

logger = setup_logger('env_validator')


def validate_environment() -> bool:
    """
    Validate all required environment variables are set

    Returns:
        True if all required variables are present, False otherwise
    """
    load_dotenv()

    required_vars: Dict[str, str] = {
        'RAPID_API_KEY': 'RapidAPI key for Zillow data',
        'FRED_API_KEY': 'FRED API key for economic indicators'
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
