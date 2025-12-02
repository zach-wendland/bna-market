"""
Reusable decorators for authentication and feature gating.

Decorators are designed to be non-breaking: when the related config flag
is disabled they simply call the underlying view without enforcing auth.
"""

import os
from functools import wraps
from typing import Callable, Optional

from flask import current_app, jsonify, request, g

from web.auth import _load_user_from_token


def _extract_token() -> Optional[str]:
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        return auth_header.replace("Bearer ", "", 1)
    return None


def require_subscription(feature: str = "default") -> Callable:
    """Require an active subscription for the wrapped view."""

    def decorator(fn: Callable) -> Callable:
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not current_app.config.get("SUBSCRIPTION_CHECKS_ENABLED", False):
                return fn(*args, **kwargs)

            token = _extract_token()
            if not token:
                return jsonify({"error": "authentication required"}), 401

            user = _load_user_from_token(token)
            if not user:
                return jsonify({"error": "invalid or expired token"}), 401

            g.current_user = user
            if user.get("subscription_status") not in {"active", "trialing"}:
                return (
                    jsonify({"error": "subscription required", "feature": feature}),
                    402,
                )

            return fn(*args, **kwargs)

        return wrapper

    return decorator


def require_auth(optional: bool = False) -> Callable:
    """Simple auth decorator for endpoints that need a logged-in user."""

    def decorator(fn: Callable) -> Callable:
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not current_app.config.get("ENABLE_AUTH_CHECKS", False):
                return fn(*args, **kwargs)

            token = _extract_token()
            if not token:
                if optional:
                    return fn(*args, **kwargs)
                return jsonify({"error": "authentication required"}), 401

            user = _load_user_from_token(token)
            if not user:
                return jsonify({"error": "invalid or expired token"}), 401

            g.current_user = user
            return fn(*args, **kwargs)

        return wrapper

    return decorator


__all__ = ["require_subscription", "require_auth"]
