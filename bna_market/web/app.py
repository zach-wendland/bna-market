"""
Flask application factory for BNA Market API

The Vue SPA handles the frontend; this Flask app only serves the /api/* endpoints.
Database operations use Supabase PostgreSQL.
"""

import os
from flask import Flask
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from bna_market.utils.logger import setup_logger

logger = setup_logger("web_app")

# Global limiter instance - configured per-app in create_app
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
)


def create_app(config=None):
    """
    Application factory for Flask app

    Args:
        config: Optional configuration dict

    Returns:
        Configured Flask application
    """
    app = Flask(__name__)

    # Override with custom config if provided
    if config:
        app.config.update(config)

    # Enable CORS for the API endpoints
    # In production, Vercel handles CORS; this is for local development
    cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
    CORS(app, origins=cors_origins, supports_credentials=True)

    # Initialize rate limiter
    # Skip rate limiting in test mode
    if not app.config.get("TESTING"):
        limiter.init_app(app)

    # Register API blueprints
    from bna_market.web.api import api_bp
    from bna_market.web.api.auth_routes import auth_bp
    from bna_market.web.api.lists_routes import lists_bp
    from bna_market.web.api.searches_routes import searches_bp
    from bna_market.web.api.crm_routes import crm_bp

    app.register_blueprint(api_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(lists_bp)
    app.register_blueprint(searches_bp)
    app.register_blueprint(crm_bp)

    logger.info("Flask app initialized with auth, lists, searches, and CRM blueprints")

    return app


# For backwards compatibility when running directly
if __name__ == "__main__":
    app = create_app()
    debug_mode = os.getenv("FLASK_DEBUG", "false").lower() in ("true", "1", "yes")
    app.run(debug=debug_mode, host="0.0.0.0", port=5000)
