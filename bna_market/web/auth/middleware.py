"""
JWT authentication middleware for Supabase Auth

This module provides decorators to protect Flask routes with JWT token verification.
Supabase Auth uses JWTs signed with the service key, which we verify on the backend.

Usage:
    from bna_market.web.auth.middleware import require_auth

    @app.route("/protected")
    @require_auth
    def protected_route():
        return jsonify({"user_id": g.user_id})
"""

from functools import wraps
from flask import request, jsonify, g
import jwt
from bna_market.core.config import settings
from bna_market.utils.logger import setup_logger

logger = setup_logger("auth_middleware")


def verify_token(token: str) -> dict:
    """
    Verify Supabase JWT token

    Supabase signs JWTs with the project's JWT secret.
    The token contains user ID (sub), email, role, and expiration.

    Args:
        token: JWT token string from Authorization header

    Returns:
        Decoded JWT payload with user information

    Raises:
        jwt.ExpiredSignatureError: Token has expired
        jwt.InvalidTokenError: Token is invalid or malformed
    """
    # Supabase uses a dedicated JWT secret for signing tokens
    secret = settings["supabase_jwt_secret"]

    if not secret:
        logger.error("SUPABASE_JWT_SECRET not configured")
        raise jwt.InvalidTokenError("Server configuration error")

    try:
        decoded = jwt.decode(
            token,
            secret,
            algorithms=["HS256"],
            audience="authenticated",
            options={"verify_aud": True}
        )

        return decoded

    except jwt.ExpiredSignatureError:
        logger.warning("Expired JWT token")
        raise
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid JWT token: {e}")
        raise


def require_auth(f):
    """
    Decorator to protect routes requiring authentication

    Expects Authorization: Bearer <token> header.
    Sets g.user_id and g.user_email on success.
    Returns 401 if token is missing, expired, or invalid.

    Example:
        @app.route("/api/lists")
        @require_auth
        def get_lists():
            user_id = g.user_id  # Available after successful auth
            return jsonify({"lists": []})
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return jsonify({"error": "Missing authorization header"}), 401

        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Invalid authorization header format"}), 401

        token = auth_header.split(" ", 1)[1]

        try:
            payload = verify_token(token)

            # Extract user information from JWT payload
            g.user_id = payload.get("sub")  # User ID (UUID)
            g.user_email = payload.get("email")
            g.user_role = payload.get("role", "authenticated")

            if not g.user_id:
                logger.error("JWT token missing 'sub' claim")
                return jsonify({"error": "Invalid token format"}), 401

            logger.debug(f"Authenticated user: {g.user_id} ({g.user_email})")

            return f(*args, **kwargs)

        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError as e:
            logger.error(f"Token verification failed: {e}")
            return jsonify({"error": "Invalid token"}), 401
        except Exception as e:
            logger.error(f"Unexpected auth error: {e}")
            return jsonify({"error": "Authentication failed"}), 500

    return decorated_function


def optional_auth(f):
    """
    Decorator that allows both authenticated and unauthenticated access

    Sets g.user_id and g.user_email if valid token is present, otherwise None.
    Does not return 401 for missing/invalid tokens.

    Useful for endpoints that behave differently for authenticated users
    but are also accessible to guests.

    Example:
        @app.route("/api/properties")
        @optional_auth
        def get_properties():
            if g.user_id:
                # Show user's favorites
                pass
            else:
                # Show public listings only
                pass
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get("Authorization")

        # Initialize as None (unauthenticated)
        g.user_id = None
        g.user_email = None
        g.user_role = None

        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1]

            try:
                payload = verify_token(token)
                g.user_id = payload.get("sub")
                g.user_email = payload.get("email")
                g.user_role = payload.get("role", "authenticated")

                logger.debug(f"Optional auth: authenticated as {g.user_id}")
            except (jwt.ExpiredSignatureError, jwt.InvalidTokenError) as e:
                logger.debug(f"Optional auth: invalid/expired token ({e})")
                # Continue with g.user_id = None

        return f(*args, **kwargs)

    return decorated_function
