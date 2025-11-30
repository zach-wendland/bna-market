"""
API Blueprint for BNA Market Application

Provides RESTful endpoints for property search, export, and metrics retrieval.
"""
from flask import Blueprint

api_bp = Blueprint('api', __name__, url_prefix='/api')

from web.api import routes
