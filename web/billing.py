"""
Billing blueprint and webhook stubs for subscription management.

This implementation is Stripe-friendly but avoids vendor lock-in by
keeping the data model simple (subscription_status and subscription_tier
on the users table). Webhook processing can be extended to verify
signatures and sync invoices once real keys are present.
"""

import json
import os
from typing import Optional

from flask import Blueprint, current_app, jsonify, request

from utils.database import get_db_connection
from config.settings import DATABASE_CONFIG

billing_bp = Blueprint("billing", __name__, url_prefix="/billing")


def update_subscription(user_id: int, status: str, tier: Optional[str] = None) -> None:
    with get_db_connection(DATABASE_CONFIG["path"]) as conn:
        conn.execute(
            """
            UPDATE users
            SET subscription_status = ?,
                subscription_tier = COALESCE(?, subscription_tier)
            WHERE id = ?
            """,
            (status, tier, user_id),
        )


@billing_bp.route("/webhook/stripe", methods=["POST"])
def stripe_webhook():
    """
    Lightweight Stripe webhook stub.

    Expects a JSON payload containing at least `type` and `data.object`
    with `customer_email` and `status`. Replace the validation logic with
    `stripe.Webhook.construct_event` when real secrets are configured.
    """

    if not os.getenv("STRIPE_WEBHOOK_SECRET"):
        current_app.logger.warning("STRIPE_WEBHOOK_SECRET not set; skipping signature validation")

    event = request.get_json(silent=True) or {}
    event_type = event.get("type")
    data_object = (event.get("data") or {}).get("object") or {}
    customer_email = data_object.get("customer_email")
    status = data_object.get("status")
    tier = data_object.get("metadata", {}).get("tier") if isinstance(data_object.get("metadata"), dict) else None

    if not customer_email or not status:
        return jsonify({"error": "missing customer_email or status"}), 400

    with get_db_connection(DATABASE_CONFIG["path"]) as conn:
        cursor = conn.execute("SELECT id FROM users WHERE email = ?", (customer_email.lower(),))
        row = cursor.fetchone()

    if not row:
        return jsonify({"error": "user not found for webhook"}), 404

    update_subscription(user_id=row[0], status=status, tier=tier)

    current_app.logger.info(f"Processed Stripe event {event_type} for user {customer_email} -> {status}")
    return jsonify({"received": True}), 200


@billing_bp.route("/plan", methods=["GET"])
def get_plan():
    """Expose current plan configuration to the front-end."""

    return jsonify(
        {
            "tiers": [
                {"name": "free", "features": ["dashboard", "api-limited"], "price": 0},
                {"name": "pro", "features": ["api", "exports"], "price": 49},
            ],
            "checkout_ready": bool(os.getenv("STRIPE_PRICE_ID")),
        }
    )


__all__ = ["billing_bp", "update_subscription"]
