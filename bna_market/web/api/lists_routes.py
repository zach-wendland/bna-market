"""
Property Lists API Routes for BNA Market Application

Users can create multiple named lists (e.g., "Downtown Condos", "Investment Properties")
and save properties to those lists.

Endpoints:
- GET /api/lists - Get all lists for current user
- POST /api/lists - Create new list
- GET /api/lists/<list_id> - Get single list with items
- PUT /api/lists/<list_id> - Update list name/description
- DELETE /api/lists/<list_id> - Delete list
- POST /api/lists/<list_id>/items - Add property to list
- DELETE /api/lists/<list_id>/items/<item_id> - Remove property from list
- PUT /api/lists/<list_id>/items/<item_id> - Update item notes
"""

from flask import Blueprint, request, jsonify, g
from bna_market.web.auth.middleware import require_auth
from bna_market.web.app import limiter
from bna_market.utils.database import get_db_connection
from bna_market.utils.logger import setup_logger
from uuid import UUID
import psycopg2.errors

logger = setup_logger("lists_api")

# Create lists blueprint
lists_bp = Blueprint("lists", __name__, url_prefix="/api/lists")


@lists_bp.route("", methods=["GET"])
@require_auth
@limiter.limit("60 per minute")
def get_user_lists():
    """
    Get all property lists for current user with item counts

    Headers:
        Authorization: Bearer <access_token>

    Returns:
        200: {
            "lists": [
                {
                    "id": "uuid",
                    "name": "Downtown Condos",
                    "description": "...",
                    "itemCount": 5,
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

            # Get lists with item counts
            cursor.execute("""
                SELECT
                    l.id, l.name, l.description, l.created_at, l.updated_at,
                    COUNT(i.id) as item_count
                FROM user_property_lists l
                LEFT JOIN user_property_list_items i ON l.id = i.list_id
                WHERE l.user_id = %s
                GROUP BY l.id, l.name, l.description, l.created_at, l.updated_at
                ORDER BY l.updated_at DESC
            """, (g.user_id,))

            columns = ['id', 'name', 'description', 'created_at', 'updated_at', 'item_count']
            lists = []
            for row in cursor.fetchall():
                list_data = dict(zip(columns, row))
                lists.append({
                    "id": str(list_data['id']),
                    "name": list_data['name'],
                    "description": list_data['description'],
                    "itemCount": list_data['item_count'],
                    "createdAt": list_data['created_at'].isoformat() if list_data['created_at'] else None,
                    "updatedAt": list_data['updated_at'].isoformat() if list_data['updated_at'] else None
                })

            logger.debug(f"Retrieved {len(lists)} lists for user {g.user_id}")

            return jsonify({"lists": lists}), 200

    except Exception as e:
        logger.error(f"Get lists error: {e}", exc_info=True)
        return jsonify({"error": "Failed to fetch lists"}), 500


@lists_bp.route("", methods=["POST"])
@require_auth
@limiter.limit("20 per hour")
def create_list():
    """
    Create new property list

    Headers:
        Authorization: Bearer <access_token>

    Request Body:
        {
            "name": "Downtown Condos",
            "description": "Potential investment properties"  # Optional
        }

    Returns:
        201: List created
        400: Invalid data (missing name, name too long)
        409: List with this name already exists
        500: Server error
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Request body is required"}), 400

        name = data.get("name", "").strip()
        description = data.get("description", "").strip()

        if not name:
            return jsonify({"error": "List name is required"}), 400

        if len(name) > 100:
            return jsonify({"error": "List name must be 100 characters or less"}), 400

        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Insert new list
            cursor.execute("""
                INSERT INTO user_property_lists (user_id, name, description)
                VALUES (%s, %s, %s)
                RETURNING id, name, description, created_at, updated_at
            """, (g.user_id, name, description or None))

            result = cursor.fetchone()

            logger.info(f"List created: {result[0]} - '{result[1]}' for user {g.user_id}")

            return jsonify({
                "id": str(result[0]),
                "name": result[1],
                "description": result[2],
                "itemCount": 0,
                "createdAt": result[3].isoformat(),
                "updatedAt": result[4].isoformat()
            }), 201

    except psycopg2.errors.UniqueViolation:
        logger.warning(f"Duplicate list name '{name}' for user {g.user_id}")
        return jsonify({"error": "A list with this name already exists"}), 409
    except Exception as e:
        logger.error(f"Create list error: {e}", exc_info=True)
        return jsonify({"error": "Failed to create list"}), 500


@lists_bp.route("/<list_id>", methods=["GET"])
@require_auth
@limiter.limit("60 per minute")
def get_list_with_items(list_id):
    """
    Get single list with all items (properties)

    Returns:
        200: List with items
        404: List not found or user doesn't own it
        500: Server error
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Get list info
            cursor.execute("""
                SELECT id, name, description, created_at, updated_at
                FROM user_property_lists
                WHERE id = %s AND user_id = %s
            """, (list_id, g.user_id))

            list_row = cursor.fetchone()

            if not list_row:
                return jsonify({"error": "List not found"}), 404

            list_data = {
                "id": str(list_row[0]),
                "name": list_row[1],
                "description": list_row[2],
                "createdAt": list_row[3].isoformat(),
                "updatedAt": list_row[4].isoformat()
            }

            # Get list items
            cursor.execute("""
                SELECT id, zpid, property_type, notes, added_at
                FROM user_property_list_items
                WHERE list_id = %s
                ORDER BY added_at DESC
            """, (list_id,))

            items = []
            for row in cursor.fetchall():
                items.append({
                    "id": str(row[0]),
                    "zpid": row[1],
                    "propertyType": row[2],
                    "notes": row[3],
                    "addedAt": row[4].isoformat()
                })

            list_data["items"] = items
            list_data["itemCount"] = len(items)

            return jsonify(list_data), 200

    except Exception as e:
        logger.error(f"Get list with items error: {e}", exc_info=True)
        return jsonify({"error": "Failed to fetch list"}), 500


@lists_bp.route("/<list_id>", methods=["PUT"])
@require_auth
@limiter.limit("30 per hour")
def update_list(list_id):
    """
    Update list name and/or description

    Request Body:
        {
            "name": "New Name",  # Optional
            "description": "New Description"  # Optional
        }

    Returns:
        200: List updated
        400: Invalid data
        404: List not found
        409: New name conflicts with existing list
        500: Server error
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Request body is required"}), 400

        name = data.get("name", "").strip() if "name" in data else None
        description = data.get("description", "").strip() if "description" in data else None

        if name is not None and len(name) > 100:
            return jsonify({"error": "List name must be 100 characters or less"}), 400

        if name is None and description is None:
            return jsonify({"error": "Provide name or description to update"}), 400

        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Build dynamic UPDATE query
            updates = []
            params = []

            if name is not None:
                updates.append("name = %s")
                params.append(name)

            if description is not None:
                updates.append("description = %s")
                params.append(description)

            params.extend([list_id, g.user_id])

            cursor.execute(f"""
                UPDATE user_property_lists
                SET {', '.join(updates)}
                WHERE id = %s AND user_id = %s
                RETURNING id, name, description, created_at, updated_at
            """, params)

            result = cursor.fetchone()

            if not result:
                return jsonify({"error": "List not found"}), 404

            logger.info(f"List updated: {list_id} for user {g.user_id}")

            return jsonify({
                "id": str(result[0]),
                "name": result[1],
                "description": result[2],
                "createdAt": result[3].isoformat(),
                "updatedAt": result[4].isoformat()
            }), 200

    except psycopg2.errors.UniqueViolation:
        return jsonify({"error": "A list with this name already exists"}), 409
    except Exception as e:
        logger.error(f"Update list error: {e}", exc_info=True)
        return jsonify({"error": "Failed to update list"}), 500


@lists_bp.route("/<list_id>", methods=["DELETE"])
@require_auth
@limiter.limit("20 per hour")
def delete_list(list_id):
    """
    Delete list (CASCADE deletes all items)

    Returns:
        200: List deleted
        404: List not found
        500: Server error
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                DELETE FROM user_property_lists
                WHERE id = %s AND user_id = %s
                RETURNING id
            """, (list_id, g.user_id))

            result = cursor.fetchone()

            if not result:
                return jsonify({"error": "List not found"}), 404

            logger.info(f"List deleted: {list_id} for user {g.user_id}")

            return jsonify({"message": "List deleted successfully"}), 200

    except Exception as e:
        logger.error(f"Delete list error: {e}", exc_info=True)
        return jsonify({"error": "Failed to delete list"}), 500


@lists_bp.route("/<list_id>/items", methods=["POST"])
@require_auth
@limiter.limit("60 per minute")
def add_property_to_list(list_id):
    """
    Add property to list

    Request Body:
        {
            "zpid": "12345",
            "propertyType": "rental",  # "rental" or "forsale"
            "notes": "Great location"  # Optional
        }

    Returns:
        201: Property added
        400: Invalid data
        404: List not found
        409: Property already in list
        500: Server error
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Request body is required"}), 400

        zpid = data.get("zpid", "").strip()
        property_type = data.get("propertyType", "").strip().lower()
        notes = data.get("notes", "").strip()

        if not zpid:
            return jsonify({"error": "zpid is required"}), 400

        if property_type not in ["rental", "forsale"]:
            return jsonify({"error": "propertyType must be 'rental' or 'forsale'"}), 400

        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Verify list ownership
            cursor.execute("""
                SELECT id FROM user_property_lists
                WHERE id = %s AND user_id = %s
            """, (list_id, g.user_id))

            if not cursor.fetchone():
                return jsonify({"error": "List not found"}), 404

            # Add property to list
            cursor.execute("""
                INSERT INTO user_property_list_items (list_id, zpid, property_type, notes)
                VALUES (%s, %s, %s, %s)
                RETURNING id, zpid, property_type, notes, added_at
            """, (list_id, zpid, property_type, notes or None))

            result = cursor.fetchone()

            logger.info(f"Property {zpid} added to list {list_id} for user {g.user_id}")

            return jsonify({
                "id": str(result[0]),
                "listId": list_id,
                "zpid": result[1],
                "propertyType": result[2],
                "notes": result[3],
                "addedAt": result[4].isoformat()
            }), 201

    except psycopg2.errors.UniqueViolation:
        return jsonify({"error": "Property already in this list"}), 409
    except Exception as e:
        logger.error(f"Add property error: {e}", exc_info=True)
        return jsonify({"error": "Failed to add property"}), 500


@lists_bp.route("/<list_id>/items/<item_id>", methods=["DELETE"])
@require_auth
@limiter.limit("60 per minute")
def remove_property_from_list(list_id, item_id):
    """
    Remove property from list

    Returns:
        200: Property removed
        404: Item not found
        500: Server error
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Verify ownership and delete
            cursor.execute("""
                DELETE FROM user_property_list_items
                WHERE id = %s AND list_id = %s
                AND list_id IN (
                    SELECT id FROM user_property_lists WHERE user_id = %s
                )
                RETURNING id
            """, (item_id, list_id, g.user_id))

            result = cursor.fetchone()

            if not result:
                return jsonify({"error": "Item not found"}), 404

            logger.info(f"Item {item_id} removed from list {list_id} for user {g.user_id}")

            return jsonify({"message": "Property removed from list"}), 200

    except Exception as e:
        logger.error(f"Remove property error: {e}", exc_info=True)
        return jsonify({"error": "Failed to remove property"}), 500


@lists_bp.route("/<list_id>/items/<item_id>", methods=["PUT"])
@require_auth
@limiter.limit("30 per hour")
def update_list_item(list_id, item_id):
    """
    Update item notes

    Request Body:
        {
            "notes": "Updated notes"
        }

    Returns:
        200: Notes updated
        400: Invalid data
        404: Item not found
        500: Server error
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Request body is required"}), 400

        notes = data.get("notes", "").strip()

        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Verify ownership and update
            cursor.execute("""
                UPDATE user_property_list_items
                SET notes = %s
                WHERE id = %s AND list_id = %s
                AND list_id IN (
                    SELECT id FROM user_property_lists WHERE user_id = %s
                )
                RETURNING id, zpid, property_type, notes, added_at
            """, (notes or None, item_id, list_id, g.user_id))

            result = cursor.fetchone()

            if not result:
                return jsonify({"error": "Item not found"}), 404

            logger.info(f"Item {item_id} notes updated for user {g.user_id}")

            return jsonify({
                "id": str(result[0]),
                "zpid": result[1],
                "propertyType": result[2],
                "notes": result[3],
                "addedAt": result[4].isoformat()
            }), 200

    except Exception as e:
        logger.error(f"Update item error: {e}", exc_info=True)
        return jsonify({"error": "Failed to update item"}), 500
