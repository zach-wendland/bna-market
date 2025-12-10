"""
Saved Searches API Routes for BNA Market Application

Users can save search filter configurations for quick recall.
Filters are stored as JSONB (minPrice, maxPrice, minBeds, maxBeds, etc.)

Endpoints:
- GET /api/searches - Get all saved searches for current user
- POST /api/searches - Save current search filters
- GET /api/searches/<search_id> - Get single saved search
- PUT /api/searches/<search_id> - Update saved search
- DELETE /api/searches/<search_id> - Delete saved search
"""

from flask import Blueprint, request, jsonify, g
from bna_market.web.auth.middleware import require_auth
from bna_market.web.app import limiter
from bna_market.utils.database import get_db_connection
from bna_market.utils.logger import setup_logger
import json
import psycopg2.errors

logger = setup_logger("searches_api")

# Create searches blueprint
searches_bp = Blueprint("searches", __name__, url_prefix="/api/searches")


@searches_bp.route("", methods=["GET"])
@require_auth
@limiter.limit("60 per minute")
def get_saved_searches():
    """
    Get all saved searches for current user

    Headers:
        Authorization: Bearer <access_token>

    Returns:
        200: {
            "searches": [
                {
                    "id": "uuid",
                    "name": "Affordable Downtown",
                    "propertyType": "rental",
                    "filters": {
                        "minPrice": 1400,
                        "maxPrice": 2000,
                        "minBeds": 2,
                        "city": "Nashville"
                    },
                    "createdAt": "2024-12-10T...",
                    "updatedAt": "..."
                }
            ]
        }
        401: Not authenticated
        500: Server error
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, name, property_type, filters, created_at, updated_at
                FROM user_saved_searches
                WHERE user_id = %s
                ORDER BY updated_at DESC
            """, (g.user_id,))

            columns = ['id', 'name', 'property_type', 'filters', 'created_at', 'updated_at']
            searches = []
            for row in cursor.fetchall():
                search_data = dict(zip(columns, row))
                searches.append({
                    "id": str(search_data['id']),
                    "name": search_data['name'],
                    "propertyType": search_data['property_type'],
                    "filters": search_data['filters'],  # JSONB is already a dict
                    "createdAt": search_data['created_at'].isoformat() if search_data['created_at'] else None,
                    "updatedAt": search_data['updated_at'].isoformat() if search_data['updated_at'] else None
                })

            logger.debug(f"Retrieved {len(searches)} saved searches for user {g.user_id}")

            return jsonify({"searches": searches}), 200

    except Exception as e:
        logger.error(f"Get saved searches error: {e}", exc_info=True)
        return jsonify({"error": "Failed to fetch saved searches"}), 500


@searches_bp.route("", methods=["POST"])
@require_auth
@limiter.limit("20 per hour")
def save_search():
    """
    Save current search filters

    Headers:
        Authorization: Bearer <access_token>

    Request Body:
        {
            "name": "Affordable Downtown",
            "propertyType": "rental",  # "rental" or "forsale"
            "filters": {
                "minPrice": 1400,
                "maxPrice": 2000,
                "minBeds": 2,
                "maxBeds": 4,
                "minBaths": 2,
                "maxBaths": 3,
                "minSqft": 1000,
                "maxSqft": 3000,
                "city": "Nashville",
                "zipCode": "37203"
            }
        }

    Returns:
        201: Search saved
        400: Invalid data (missing name, invalid property type)
        409: Search with this name already exists
        500: Server error
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Request body is required"}), 400

        name = data.get("name", "").strip()
        property_type = data.get("propertyType", "").strip().lower()
        filters = data.get("filters", {})

        if not name:
            return jsonify({"error": "Search name is required"}), 400

        if len(name) > 100:
            return jsonify({"error": "Search name must be 100 characters or less"}), 400

        if property_type not in ["rental", "forsale"]:
            return jsonify({"error": "propertyType must be 'rental' or 'forsale'"}), 400

        if not isinstance(filters, dict):
            return jsonify({"error": "filters must be an object"}), 400

        # Validate filter keys (optional - ensures only valid filters are saved)
        valid_filter_keys = {
            'minPrice', 'maxPrice', 'minBeds', 'maxBeds',
            'minBaths', 'maxBaths', 'minSqft', 'maxSqft',
            'city', 'zipCode'
        }
        invalid_keys = set(filters.keys()) - valid_filter_keys
        if invalid_keys:
            logger.warning(f"Invalid filter keys: {invalid_keys}")
            # Remove invalid keys instead of rejecting
            filters = {k: v for k, v in filters.items() if k in valid_filter_keys}

        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Insert new saved search
            cursor.execute("""
                INSERT INTO user_saved_searches (user_id, name, property_type, filters)
                VALUES (%s, %s, %s, %s::jsonb)
                RETURNING id, name, property_type, filters, created_at, updated_at
            """, (g.user_id, name, property_type, json.dumps(filters)))

            result = cursor.fetchone()

            logger.info(f"Search saved: {result[0]} - '{result[1]}' for user {g.user_id}")

            return jsonify({
                "id": str(result[0]),
                "name": result[1],
                "propertyType": result[2],
                "filters": result[3],
                "createdAt": result[4].isoformat(),
                "updatedAt": result[5].isoformat()
            }), 201

    except psycopg2.errors.UniqueViolation:
        logger.warning(f"Duplicate search name '{name}' for user {g.user_id}")
        return jsonify({"error": "A search with this name already exists"}), 409
    except Exception as e:
        logger.error(f"Save search error: {e}", exc_info=True)
        return jsonify({"error": "Failed to save search"}), 500


@searches_bp.route("/<search_id>", methods=["GET"])
@require_auth
@limiter.limit("60 per minute")
def get_saved_search(search_id):
    """
    Get single saved search

    Returns:
        200: Saved search data
        404: Search not found or user doesn't own it
        500: Server error
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, name, property_type, filters, created_at, updated_at
                FROM user_saved_searches
                WHERE id = %s AND user_id = %s
            """, (search_id, g.user_id))

            result = cursor.fetchone()

            if not result:
                return jsonify({"error": "Search not found"}), 404

            return jsonify({
                "id": str(result[0]),
                "name": result[1],
                "propertyType": result[2],
                "filters": result[3],
                "createdAt": result[4].isoformat(),
                "updatedAt": result[5].isoformat()
            }), 200

    except Exception as e:
        logger.error(f"Get saved search error: {e}", exc_info=True)
        return jsonify({"error": "Failed to fetch search"}), 500


@searches_bp.route("/<search_id>", methods=["PUT"])
@require_auth
@limiter.limit("30 per hour")
def update_saved_search(search_id):
    """
    Update saved search name and/or filters

    Request Body:
        {
            "name": "New Name",  # Optional
            "filters": {...}  # Optional
        }

    Returns:
        200: Search updated
        400: Invalid data
        404: Search not found
        409: New name conflicts with existing search
        500: Server error
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Request body is required"}), 400

        name = data.get("name", "").strip() if "name" in data else None
        filters = data.get("filters") if "filters" in data else None

        if name is not None and len(name) > 100:
            return jsonify({"error": "Search name must be 100 characters or less"}), 400

        if name is None and filters is None:
            return jsonify({"error": "Provide name or filters to update"}), 400

        if filters is not None and not isinstance(filters, dict):
            return jsonify({"error": "filters must be an object"}), 400

        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Build dynamic UPDATE query
            updates = []
            params = []

            if name is not None:
                updates.append("name = %s")
                params.append(name)

            if filters is not None:
                updates.append("filters = %s::jsonb")
                params.append(json.dumps(filters))

            params.extend([search_id, g.user_id])

            cursor.execute(f"""
                UPDATE user_saved_searches
                SET {', '.join(updates)}
                WHERE id = %s AND user_id = %s
                RETURNING id, name, property_type, filters, created_at, updated_at
            """, params)

            result = cursor.fetchone()

            if not result:
                return jsonify({"error": "Search not found"}), 404

            logger.info(f"Search updated: {search_id} for user {g.user_id}")

            return jsonify({
                "id": str(result[0]),
                "name": result[1],
                "propertyType": result[2],
                "filters": result[3],
                "createdAt": result[4].isoformat(),
                "updatedAt": result[5].isoformat()
            }), 200

    except psycopg2.errors.UniqueViolation:
        return jsonify({"error": "A search with this name already exists"}), 409
    except Exception as e:
        logger.error(f"Update search error: {e}", exc_info=True)
        return jsonify({"error": "Failed to update search"}), 500


@searches_bp.route("/<search_id>", methods=["DELETE"])
@require_auth
@limiter.limit("20 per hour")
def delete_saved_search(search_id):
    """
    Delete saved search

    Returns:
        200: Search deleted
        404: Search not found
        500: Server error
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                DELETE FROM user_saved_searches
                WHERE id = %s AND user_id = %s
                RETURNING id
            """, (search_id, g.user_id))

            result = cursor.fetchone()

            if not result:
                return jsonify({"error": "Search not found"}), 404

            logger.info(f"Search deleted: {search_id} for user {g.user_id}")

            return jsonify({"message": "Search deleted successfully"}), 200

    except Exception as e:
        logger.error(f"Delete search error: {e}", exc_info=True)
        return jsonify({"error": "Failed to delete search"}), 500
