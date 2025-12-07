"""
Flask application factory for BNA Market API

The Vue SPA handles the frontend; this Flask app only serves the /api/* endpoints.
"""

from flask import Flask

from bna_market.utils.logger import setup_logger
from bna_market.core.config import DATABASE_CONFIG

logger = setup_logger("web_app")


def create_app(config=None):
    """
    Application factory for Flask app

    Args:
        config: Optional configuration dict

    Returns:
        Configured Flask application
    """
    app = Flask(__name__)

    # Default configuration from settings
    app.config["DATABASE_PATH"] = DATABASE_CONFIG["path"]

    # Override with custom config if provided
    if config:
        app.config.update(config)

    # Register API blueprints
    from bna_market.web.api import api_bp
    app.register_blueprint(api_bp)

    return app


# For backwards compatibility when running directly
if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=5000)
