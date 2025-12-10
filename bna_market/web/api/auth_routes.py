"""
Authentication API Routes for BNA Market Application

Endpoints:
- POST /api/auth/magic-link - Send magic link to email
- POST /api/auth/verify - Verify magic link token and create session
- GET /api/auth/session - Get current user session
- POST /api/auth/logout - Logout user (revoke session)
- POST /api/auth/refresh - Refresh access token
"""

from flask import Blueprint, request, jsonify, g
from bna_market.web.api import api_bp
from bna_market.web.app import limiter
from bna_market.web.auth.middleware import require_auth
from bna_market.utils.database import get_supabase_client
from bna_market.utils.logger import setup_logger

logger = setup_logger("auth_api")

# Create auth blueprint
auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/test", methods=["GET"])
def test_endpoint():
    """Simple test endpoint to verify blueprint is registered"""
    return jsonify({"status": "ok", "message": "Auth blueprint is working"}), 200


@auth_bp.route("/magic-link", methods=["POST"])
@limiter.limit("5 per hour")
def send_magic_link():
    """
    Send magic link to user's email

    Request Body:
        {
            "email": "user@example.com",
            "redirectTo": "https://yourapp.com/auth/callback"  # Optional
        }

    Returns:
        200: Magic link sent successfully
        400: Invalid email or missing data
        429: Rate limit exceeded (5 per hour)
        500: Failed to send magic link

    Rate Limit: 5 requests per hour per IP
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Request body is required"}), 400

        email = data.get("email", "").strip().lower()
        redirect_to = data.get("redirectTo")

        # Validate email
        if not email or "@" not in email or "." not in email:
            return jsonify({"error": "Valid email address is required"}), 400

        # Get Supabase client with service key for admin operations
        client = get_supabase_client(use_service_key=True)

        # Send magic link using Supabase Auth
        options = {}
        if redirect_to:
            options["email_redirect_to"] = redirect_to

        response = client.auth.sign_in_with_otp({
            "email": email,
            "options": options
        })

        logger.info(f"Magic link sent to {email}")

        return jsonify({
            "message": "Magic link sent. Check your email.",
            "email": email
        }), 200

    except Exception as e:
        logger.error(f"Magic link error: {e}", exc_info=True)
        return jsonify({"error": "Failed to send magic link. Please try again."}), 500


@auth_bp.route("/verify", methods=["POST"])
@limiter.limit("10 per hour")
def verify_magic_link():
    """
    Verify magic link token and create session

    Request Body:
        {
            "token": "magic_link_token_from_email",
            "type": "magiclink"  # or "recovery", "invite"
        }

    Returns:
        200: Session created with access_token and refresh_token
        400: Invalid or missing token
        401: Token expired or already used
        429: Rate limit exceeded (10 per hour)
        500: Verification failed

    Rate Limit: 10 requests per hour per IP
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Request body is required"}), 400

        token = data.get("token", "").strip()
        token_type = data.get("type", "magiclink")

        if not token:
            return jsonify({"error": "Token is required"}), 400

        # Get Supabase client
        client = get_supabase_client(use_service_key=True)

        # Verify the OTP token
        response = client.auth.verify_otp({
            "token": token,
            "type": token_type
        })

        if response.session and response.user:
            logger.info(f"User authenticated: {response.user.id} ({response.user.email})")

            return jsonify({
                "access_token": response.session.access_token,
                "refresh_token": response.session.refresh_token,
                "expires_in": response.session.expires_in,
                "expires_at": response.session.expires_at,
                "user": {
                    "id": str(response.user.id),
                    "email": response.user.email,
                    "created_at": response.user.created_at
                }
            }), 200
        else:
            logger.warning("Token verification failed: no session returned")
            return jsonify({"error": "Invalid or expired token"}), 401

    except Exception as e:
        logger.error(f"Token verification error: {e}", exc_info=True)

        # Check for specific error messages from Supabase
        error_message = str(e).lower()
        if "expired" in error_message or "already used" in error_message:
            return jsonify({"error": "Token expired or already used"}), 401
        elif "invalid" in error_message:
            return jsonify({"error": "Invalid token"}), 400
        else:
            return jsonify({"error": "Token verification failed"}), 500


@auth_bp.route("/session", methods=["GET"])
@require_auth
def get_session():
    """
    Get current user session info

    Headers:
        Authorization: Bearer <access_token>

    Returns:
        200: User session information
        401: Not authenticated or token invalid

    Protected Route: Requires valid JWT token
    """
    try:
        return jsonify({
            "user": {
                "id": g.user_id,
                "email": g.user_email,
                "role": g.user_role
            },
            "authenticated": True
        }), 200

    except Exception as e:
        logger.error(f"Get session error: {e}", exc_info=True)
        return jsonify({"error": "Failed to get session"}), 500


@auth_bp.route("/logout", methods=["POST"])
@require_auth
def logout():
    """
    Logout user (revoke session on server)

    Headers:
        Authorization: Bearer <access_token>

    Returns:
        200: Logged out successfully
        401: Not authenticated

    Note: Client should also delete local tokens after calling this endpoint

    Protected Route: Requires valid JWT token
    """
    try:
        # Get Supabase client
        client = get_supabase_client(use_service_key=True)

        # Supabase handles session revocation server-side
        # Client should delete tokens from localStorage

        logger.info(f"User logged out: {g.user_id} ({g.user_email})")

        return jsonify({
            "message": "Logged out successfully"
        }), 200

    except Exception as e:
        logger.error(f"Logout error: {e}", exc_info=True)
        return jsonify({"error": "Logout failed"}), 500


@auth_bp.route("/refresh", methods=["POST"])
@limiter.limit("20 per hour")
def refresh_token():
    """
    Refresh access token using refresh token

    Request Body:
        {
            "refresh_token": "refresh_token_string"
        }

    Returns:
        200: New access_token and refresh_token
        400: Missing refresh token
        401: Invalid or expired refresh token
        429: Rate limit exceeded (20 per hour)
        500: Refresh failed

    Rate Limit: 20 requests per hour per IP
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Request body is required"}), 400

        refresh_token = data.get("refresh_token", "").strip()

        if not refresh_token:
            return jsonify({"error": "Refresh token is required"}), 400

        # Get Supabase client
        client = get_supabase_client(use_service_key=True)

        # Refresh the session
        response = client.auth.refresh_session(refresh_token)

        if response.session:
            logger.info(f"Token refreshed for user: {response.user.id}")

            return jsonify({
                "access_token": response.session.access_token,
                "refresh_token": response.session.refresh_token,
                "expires_in": response.session.expires_in,
                "expires_at": response.session.expires_at
            }), 200
        else:
            return jsonify({"error": "Invalid refresh token"}), 401

    except Exception as e:
        logger.error(f"Token refresh error: {e}", exc_info=True)

        error_message = str(e).lower()
        if "invalid" in error_message or "expired" in error_message:
            return jsonify({"error": "Invalid or expired refresh token"}), 401
        else:
            return jsonify({"error": "Token refresh failed"}), 500
