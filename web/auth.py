"""
Authentication blueprint and helpers for the SaaS layer.

This module keeps the implementation lightweight so the existing Flask
application can opt-in to authentication without breaking current
functionality. Tokens are issued using itsdangerous (bundled with Flask)
and a simple SQLite-backed user table.
"""

import os
import sqlite3
from datetime import datetime
from typing import Dict, Optional

from flask import Blueprint, current_app, jsonify, request
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from werkzeug.security import check_password_hash, generate_password_hash

from utils.database import get_db_connection
from config.settings import DATABASE_CONFIG

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


def _serializer(secret_key: str) -> URLSafeTimedSerializer:
    return URLSafeTimedSerializer(secret_key, salt="bna-market-auth")


def init_user_table() -> None:
    """Create the users table if it does not already exist."""

    with get_db_connection(DATABASE_CONFIG["path"]) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                subscription_status TEXT DEFAULT 'trialing',
                subscription_tier TEXT DEFAULT 'free',
                created_at TEXT NOT NULL
            );
            """
        )


def _generate_token(email: str, user_id: int) -> str:
    secret = current_app.config.get("SECRET_KEY", os.getenv("SECRET_KEY", "dev-secret"))
    serializer = _serializer(secret)
    max_age = int(os.getenv("AUTH_TOKEN_TTL", "86400"))  # 24h default
    return serializer.dumps({"email": email, "user_id": user_id, "exp": max_age})


def _load_user_from_token(token: str) -> Optional[Dict]:
    secret = current_app.config.get("SECRET_KEY", os.getenv("SECRET_KEY", "dev-secret"))
    serializer = _serializer(secret)
    max_age = int(os.getenv("AUTH_TOKEN_TTL", "86400"))
    try:
        payload = serializer.loads(token, max_age=max_age)
    except (BadSignature, SignatureExpired):
        return None

    with get_db_connection(DATABASE_CONFIG["path"]) as conn:
        cursor = conn.execute("SELECT id, email, subscription_status, subscription_tier FROM users WHERE id = ?", (payload["user_id"],))
        row = cursor.fetchone()
        if not row:
            return None
        return {
            "id": row[0],
            "email": row[1],
            "subscription_status": row[2],
            "subscription_tier": row[3],
        }


def _create_user(email: str, password: str) -> int:
    hashed_pw = generate_password_hash(password)
    created_at = datetime.utcnow().isoformat()
    with get_db_connection(DATABASE_CONFIG["path"]) as conn:
        cursor = conn.execute(
            "INSERT INTO users (email, password_hash, created_at) VALUES (?, ?, ?)",
            (email.lower(), hashed_pw, created_at),
        )
        return cursor.lastrowid


@auth_bp.route("/signup", methods=["POST"])
def signup():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "email and password are required"}), 400

    try:
        user_id = _create_user(email=email, password=password)
    except sqlite3.IntegrityError:
        return jsonify({"error": "user already exists"}), 409

    token = _generate_token(email=email, user_id=user_id)
    return jsonify({"token": token, "user_id": user_id}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "email and password are required"}), 400

    with get_db_connection(DATABASE_CONFIG["path"]) as conn:
        cursor = conn.execute(
            "SELECT id, password_hash FROM users WHERE email = ?",
            (email.lower(),),
        )
        row = cursor.fetchone()

    if not row or not check_password_hash(row[1], password):
        return jsonify({"error": "invalid credentials"}), 401

    token = _generate_token(email=email, user_id=row[0])
    return jsonify({"token": token, "user_id": row[0]}), 200


@auth_bp.route("/me", methods=["GET"])
def current_user():
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "") if auth_header.startswith("Bearer ") else None

    if not token:
        return jsonify({"error": "missing token"}), 401

    user = _load_user_from_token(token)
    if not user:
        return jsonify({"error": "invalid or expired token"}), 401

    return jsonify({"user": user}), 200


__all__ = ["auth_bp", "init_user_table", "_load_user_from_token"]
