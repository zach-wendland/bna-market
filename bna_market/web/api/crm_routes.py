"""
CRM API Routes for BNA Market Application

Provides lead management, search alerts, property comps, and portfolio management.

Endpoints:
- Leads: CRUD operations for CRM leads
- Alerts: Search notification settings
- Comps: Property comparison analyses
- Portfolios: Investment portfolio management
"""

from flask import Blueprint, request, jsonify, g
from bna_market.web.auth.middleware import require_auth
from bna_market.web.app import limiter
from bna_market.utils.database import get_db_connection
from bna_market.utils.logger import setup_logger
import psycopg2.errors

logger = setup_logger("crm_api")

# Create CRM blueprint
crm_bp = Blueprint("crm", __name__, url_prefix="/api/crm")


# ============================================================================
# LEADS ENDPOINTS
# ============================================================================

@crm_bp.route("/leads", methods=["GET"])
@require_auth
@limiter.limit("60 per minute")
def get_leads():
    """
    Get all leads for current user with optional filters

    Query Params:
        status: Filter by status (new, contacted, qualified, converted, lost)
        tag: Filter by tag

    Returns:
        200: { "leads": [...] }
    """
    try:
        status = request.args.get("status")
        tag = request.args.get("tag")

        with get_db_connection() as conn:
            cursor = conn.cursor()

            query = """
                SELECT id, property_zpid, name, email, phone, message,
                       status, assigned_to, tags, next_follow_up_date, notes,
                       created_at, updated_at
                FROM crm_leads
                WHERE user_id = %s
            """
            params = [g.user_id]

            if status:
                query += " AND status = %s"
                params.append(status)

            if tag:
                query += " AND %s = ANY(tags)"
                params.append(tag)

            query += " ORDER BY updated_at DESC"

            cursor.execute(query, params)

            columns = ['id', 'property_zpid', 'name', 'email', 'phone', 'message',
                       'status', 'assigned_to', 'tags', 'next_follow_up_date', 'notes',
                       'created_at', 'updated_at']

            leads = []
            for row in cursor.fetchall():
                lead = dict(zip(columns, row))
                leads.append({
                    "id": str(lead['id']),
                    "propertyZpid": lead['property_zpid'],
                    "name": lead['name'],
                    "email": lead['email'],
                    "phone": lead['phone'],
                    "message": lead['message'],
                    "status": lead['status'],
                    "assignedTo": str(lead['assigned_to']) if lead['assigned_to'] else None,
                    "tags": lead['tags'] or [],
                    "nextFollowUpDate": lead['next_follow_up_date'].isoformat() if lead['next_follow_up_date'] else None,
                    "notes": lead['notes'],
                    "createdAt": lead['created_at'].isoformat(),
                    "updatedAt": lead['updated_at'].isoformat()
                })

            return jsonify({"leads": leads}), 200

    except Exception as e:
        logger.error(f"Get leads error: {e}", exc_info=True)
        return jsonify({"error": "Failed to fetch leads"}), 500


@crm_bp.route("/leads", methods=["POST"])
@require_auth
@limiter.limit("30 per hour")
def create_lead():
    """
    Create new lead

    Request Body:
        {
            "propertyZpid": "12345",
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "555-1234",
            "message": "Interested in this property",
            "tags": ["hot", "investor"]
        }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Request body is required"}), 400

        required = ["propertyZpid", "name", "email"]
        for field in required:
            if not data.get(field):
                return jsonify({"error": f"{field} is required"}), 400

        with get_db_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO crm_leads (user_id, property_zpid, name, email, phone, message, tags)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id, property_zpid, name, email, phone, message,
                          status, tags, created_at, updated_at
            """, (
                g.user_id,
                data["propertyZpid"],
                data["name"],
                data["email"],
                data.get("phone"),
                data.get("message"),
                data.get("tags", [])
            ))

            result = cursor.fetchone()

            logger.info(f"Lead created: {result[0]} for user {g.user_id}")

            return jsonify({
                "id": str(result[0]),
                "propertyZpid": result[1],
                "name": result[2],
                "email": result[3],
                "phone": result[4],
                "message": result[5],
                "status": result[6],
                "tags": result[7] or [],
                "createdAt": result[8].isoformat(),
                "updatedAt": result[9].isoformat()
            }), 201

    except Exception as e:
        logger.error(f"Create lead error: {e}", exc_info=True)
        return jsonify({"error": "Failed to create lead"}), 500


@crm_bp.route("/leads/<lead_id>", methods=["GET"])
@require_auth
@limiter.limit("60 per minute")
def get_lead(lead_id):
    """Get single lead details"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, property_zpid, name, email, phone, message,
                       status, assigned_to, tags, next_follow_up_date, notes,
                       created_at, updated_at
                FROM crm_leads
                WHERE id = %s AND user_id = %s
            """, (lead_id, g.user_id))

            row = cursor.fetchone()

            if not row:
                return jsonify({"error": "Lead not found"}), 404

            columns = ['id', 'property_zpid', 'name', 'email', 'phone', 'message',
                       'status', 'assigned_to', 'tags', 'next_follow_up_date', 'notes',
                       'created_at', 'updated_at']
            lead = dict(zip(columns, row))

            return jsonify({
                "id": str(lead['id']),
                "propertyZpid": lead['property_zpid'],
                "name": lead['name'],
                "email": lead['email'],
                "phone": lead['phone'],
                "message": lead['message'],
                "status": lead['status'],
                "assignedTo": str(lead['assigned_to']) if lead['assigned_to'] else None,
                "tags": lead['tags'] or [],
                "nextFollowUpDate": lead['next_follow_up_date'].isoformat() if lead['next_follow_up_date'] else None,
                "notes": lead['notes'],
                "createdAt": lead['created_at'].isoformat(),
                "updatedAt": lead['updated_at'].isoformat()
            }), 200

    except Exception as e:
        logger.error(f"Get lead error: {e}", exc_info=True)
        return jsonify({"error": "Failed to fetch lead"}), 500


@crm_bp.route("/leads/<lead_id>", methods=["PUT"])
@require_auth
@limiter.limit("30 per hour")
def update_lead(lead_id):
    """
    Update lead

    Request Body (all optional):
        {
            "status": "contacted",
            "tags": ["hot"],
            "notes": "Called on Monday",
            "nextFollowUpDate": "2024-12-20"
        }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Request body is required"}), 400

        with get_db_connection() as conn:
            cursor = conn.cursor()

            updates = []
            params = []

            if "status" in data:
                updates.append("status = %s")
                params.append(data["status"])

            if "tags" in data:
                updates.append("tags = %s")
                params.append(data["tags"])

            if "notes" in data:
                updates.append("notes = %s")
                params.append(data["notes"])

            if "nextFollowUpDate" in data:
                updates.append("next_follow_up_date = %s")
                params.append(data["nextFollowUpDate"])

            if not updates:
                return jsonify({"error": "No fields to update"}), 400

            params.extend([lead_id, g.user_id])

            cursor.execute(f"""
                UPDATE crm_leads
                SET {', '.join(updates)}
                WHERE id = %s AND user_id = %s
                RETURNING id, property_zpid, name, email, status, tags,
                          next_follow_up_date, notes, updated_at
            """, params)

            result = cursor.fetchone()

            if not result:
                return jsonify({"error": "Lead not found"}), 404

            logger.info(f"Lead updated: {lead_id} for user {g.user_id}")

            return jsonify({
                "id": str(result[0]),
                "propertyZpid": result[1],
                "name": result[2],
                "email": result[3],
                "status": result[4],
                "tags": result[5] or [],
                "nextFollowUpDate": result[6].isoformat() if result[6] else None,
                "notes": result[7],
                "updatedAt": result[8].isoformat()
            }), 200

    except Exception as e:
        logger.error(f"Update lead error: {e}", exc_info=True)
        return jsonify({"error": "Failed to update lead"}), 500


@crm_bp.route("/leads/<lead_id>", methods=["DELETE"])
@require_auth
@limiter.limit("20 per hour")
def delete_lead(lead_id):
    """Delete lead"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                DELETE FROM crm_leads
                WHERE id = %s AND user_id = %s
                RETURNING id
            """, (lead_id, g.user_id))

            if not cursor.fetchone():
                return jsonify({"error": "Lead not found"}), 404

            logger.info(f"Lead deleted: {lead_id} for user {g.user_id}")

            return jsonify({"message": "Lead deleted successfully"}), 200

    except Exception as e:
        logger.error(f"Delete lead error: {e}", exc_info=True)
        return jsonify({"error": "Failed to delete lead"}), 500


# ============================================================================
# ALERTS ENDPOINTS
# ============================================================================

@crm_bp.route("/alerts", methods=["GET"])
@require_auth
@limiter.limit("60 per minute")
def get_alerts():
    """Get all search alerts for current user"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT a.id, a.saved_search_id, a.alert_type, a.enabled,
                       a.frequency, a.last_sent_at, a.created_at, a.updated_at,
                       s.name as search_name
                FROM search_alerts a
                LEFT JOIN user_saved_searches s ON a.saved_search_id = s.id
                WHERE a.user_id = %s
                ORDER BY a.created_at DESC
            """, (g.user_id,))

            alerts = []
            for row in cursor.fetchall():
                alerts.append({
                    "id": str(row[0]),
                    "savedSearchId": str(row[1]) if row[1] else None,
                    "alertType": row[2],
                    "enabled": row[3],
                    "frequency": row[4],
                    "lastSentAt": row[5].isoformat() if row[5] else None,
                    "createdAt": row[6].isoformat(),
                    "updatedAt": row[7].isoformat(),
                    "searchName": row[8]
                })

            return jsonify({"alerts": alerts}), 200

    except Exception as e:
        logger.error(f"Get alerts error: {e}", exc_info=True)
        return jsonify({"error": "Failed to fetch alerts"}), 500


@crm_bp.route("/alerts", methods=["POST"])
@require_auth
@limiter.limit("20 per hour")
def create_alert():
    """
    Create new search alert

    Request Body:
        {
            "savedSearchId": "uuid",
            "alertType": "email",
            "frequency": "daily"
        }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Request body is required"}), 400

        if not data.get("savedSearchId"):
            return jsonify({"error": "savedSearchId is required"}), 400

        alert_type = data.get("alertType", "email")
        if alert_type not in ["email", "sms", "both"]:
            return jsonify({"error": "alertType must be 'email', 'sms', or 'both'"}), 400

        frequency = data.get("frequency", "daily")
        if frequency not in ["instant", "daily", "weekly"]:
            return jsonify({"error": "frequency must be 'instant', 'daily', or 'weekly'"}), 400

        with get_db_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO search_alerts (user_id, saved_search_id, alert_type, frequency)
                VALUES (%s, %s, %s, %s)
                RETURNING id, saved_search_id, alert_type, enabled, frequency, created_at
            """, (g.user_id, data["savedSearchId"], alert_type, frequency))

            result = cursor.fetchone()

            logger.info(f"Alert created: {result[0]} for user {g.user_id}")

            return jsonify({
                "id": str(result[0]),
                "savedSearchId": str(result[1]),
                "alertType": result[2],
                "enabled": result[3],
                "frequency": result[4],
                "createdAt": result[5].isoformat()
            }), 201

    except psycopg2.errors.UniqueViolation:
        return jsonify({"error": "Alert already exists for this search and type"}), 409
    except Exception as e:
        logger.error(f"Create alert error: {e}", exc_info=True)
        return jsonify({"error": "Failed to create alert"}), 500


@crm_bp.route("/alerts/<alert_id>", methods=["PUT"])
@require_auth
@limiter.limit("30 per hour")
def update_alert(alert_id):
    """Update alert settings (enabled, frequency)"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Request body is required"}), 400

        with get_db_connection() as conn:
            cursor = conn.cursor()

            updates = []
            params = []

            if "enabled" in data:
                updates.append("enabled = %s")
                params.append(data["enabled"])

            if "frequency" in data:
                if data["frequency"] not in ["instant", "daily", "weekly"]:
                    return jsonify({"error": "Invalid frequency"}), 400
                updates.append("frequency = %s")
                params.append(data["frequency"])

            if not updates:
                return jsonify({"error": "No fields to update"}), 400

            params.extend([alert_id, g.user_id])

            cursor.execute(f"""
                UPDATE search_alerts
                SET {', '.join(updates)}
                WHERE id = %s AND user_id = %s
                RETURNING id, enabled, frequency, updated_at
            """, params)

            result = cursor.fetchone()

            if not result:
                return jsonify({"error": "Alert not found"}), 404

            return jsonify({
                "id": str(result[0]),
                "enabled": result[1],
                "frequency": result[2],
                "updatedAt": result[3].isoformat()
            }), 200

    except Exception as e:
        logger.error(f"Update alert error: {e}", exc_info=True)
        return jsonify({"error": "Failed to update alert"}), 500


@crm_bp.route("/alerts/<alert_id>", methods=["DELETE"])
@require_auth
@limiter.limit("20 per hour")
def delete_alert(alert_id):
    """Delete search alert"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                DELETE FROM search_alerts
                WHERE id = %s AND user_id = %s
                RETURNING id
            """, (alert_id, g.user_id))

            if not cursor.fetchone():
                return jsonify({"error": "Alert not found"}), 404

            return jsonify({"message": "Alert deleted successfully"}), 200

    except Exception as e:
        logger.error(f"Delete alert error: {e}", exc_info=True)
        return jsonify({"error": "Failed to delete alert"}), 500


# ============================================================================
# COMPS ENDPOINTS
# ============================================================================

@crm_bp.route("/comps", methods=["GET"])
@require_auth
@limiter.limit("60 per minute")
def get_comps():
    """Get all property comparisons for current user"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, name, subject_zpid, comp_zpids, filters, notes,
                       created_at, updated_at
                FROM property_comps
                WHERE user_id = %s
                ORDER BY updated_at DESC
            """, (g.user_id,))

            comps = []
            for row in cursor.fetchall():
                comps.append({
                    "id": str(row[0]),
                    "name": row[1],
                    "subjectZpid": row[2],
                    "compZpids": row[3] or [],
                    "filters": row[4],
                    "notes": row[5],
                    "compCount": len(row[3] or []),
                    "createdAt": row[6].isoformat(),
                    "updatedAt": row[7].isoformat()
                })

            return jsonify({"comps": comps}), 200

    except Exception as e:
        logger.error(f"Get comps error: {e}", exc_info=True)
        return jsonify({"error": "Failed to fetch comps"}), 500


@crm_bp.route("/comps", methods=["POST"])
@require_auth
@limiter.limit("20 per hour")
def create_comp():
    """
    Create new property comparison

    Request Body:
        {
            "name": "Downtown Analysis",
            "subjectZpid": "12345",
            "compZpids": ["23456", "34567"],
            "filters": { "maxDistance": 1, "maxPriceDiff": 10 },
            "notes": "Analysis notes"
        }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Request body is required"}), 400

        required = ["name", "subjectZpid", "compZpids"]
        for field in required:
            if not data.get(field):
                return jsonify({"error": f"{field} is required"}), 400

        with get_db_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO property_comps (user_id, name, subject_zpid, comp_zpids, filters, notes)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id, name, subject_zpid, comp_zpids, filters, notes, created_at, updated_at
            """, (
                g.user_id,
                data["name"],
                data["subjectZpid"],
                data["compZpids"],
                data.get("filters"),
                data.get("notes")
            ))

            result = cursor.fetchone()

            logger.info(f"Comp created: {result[0]} for user {g.user_id}")

            return jsonify({
                "id": str(result[0]),
                "name": result[1],
                "subjectZpid": result[2],
                "compZpids": result[3] or [],
                "filters": result[4],
                "notes": result[5],
                "createdAt": result[6].isoformat(),
                "updatedAt": result[7].isoformat()
            }), 201

    except psycopg2.errors.UniqueViolation:
        return jsonify({"error": "A comparison with this name already exists"}), 409
    except Exception as e:
        logger.error(f"Create comp error: {e}", exc_info=True)
        return jsonify({"error": "Failed to create comparison"}), 500


@crm_bp.route("/comps/<comp_id>", methods=["GET"])
@require_auth
@limiter.limit("60 per minute")
def get_comp(comp_id):
    """Get single comparison with details"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, name, subject_zpid, comp_zpids, filters, notes,
                       created_at, updated_at
                FROM property_comps
                WHERE id = %s AND user_id = %s
            """, (comp_id, g.user_id))

            row = cursor.fetchone()

            if not row:
                return jsonify({"error": "Comparison not found"}), 404

            return jsonify({
                "id": str(row[0]),
                "name": row[1],
                "subjectZpid": row[2],
                "compZpids": row[3] or [],
                "filters": row[4],
                "notes": row[5],
                "createdAt": row[6].isoformat(),
                "updatedAt": row[7].isoformat()
            }), 200

    except Exception as e:
        logger.error(f"Get comp error: {e}", exc_info=True)
        return jsonify({"error": "Failed to fetch comparison"}), 500


@crm_bp.route("/comps/<comp_id>", methods=["DELETE"])
@require_auth
@limiter.limit("20 per hour")
def delete_comp(comp_id):
    """Delete comparison"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                DELETE FROM property_comps
                WHERE id = %s AND user_id = %s
                RETURNING id
            """, (comp_id, g.user_id))

            if not cursor.fetchone():
                return jsonify({"error": "Comparison not found"}), 404

            return jsonify({"message": "Comparison deleted successfully"}), 200

    except Exception as e:
        logger.error(f"Delete comp error: {e}", exc_info=True)
        return jsonify({"error": "Failed to delete comparison"}), 500


# ============================================================================
# PORTFOLIOS ENDPOINTS
# ============================================================================

@crm_bp.route("/portfolios", methods=["GET"])
@require_auth
@limiter.limit("60 per minute")
def get_portfolios():
    """Get all portfolios for current user with aggregated metrics"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT p.id, p.name, p.description, p.target_return,
                       p.created_at, p.updated_at,
                       COUNT(pp.id) as property_count,
                       COALESCE(SUM(pp.current_value), 0) as total_value,
                       COALESCE(SUM(pp.monthly_rent), 0) as total_rent,
                       COALESCE(SUM(pp.monthly_expenses), 0) as total_expenses,
                       COUNT(CASE WHEN pp.is_vacant THEN 1 END) as vacant_count
                FROM user_portfolios p
                LEFT JOIN portfolio_properties pp ON p.id = pp.portfolio_id
                WHERE p.user_id = %s
                GROUP BY p.id
                ORDER BY p.updated_at DESC
            """, (g.user_id,))

            portfolios = []
            for row in cursor.fetchall():
                monthly_cash_flow = float(row[8] or 0) - float(row[9] or 0)
                portfolios.append({
                    "id": str(row[0]),
                    "name": row[1],
                    "description": row[2],
                    "targetReturn": float(row[3]) if row[3] else None,
                    "createdAt": row[4].isoformat(),
                    "updatedAt": row[5].isoformat(),
                    "propertyCount": row[6],
                    "totalValue": float(row[7]),
                    "totalRent": float(row[8]),
                    "totalExpenses": float(row[9]),
                    "vacantCount": row[10],
                    "monthlyCashFlow": monthly_cash_flow
                })

            return jsonify({"portfolios": portfolios}), 200

    except Exception as e:
        logger.error(f"Get portfolios error: {e}", exc_info=True)
        return jsonify({"error": "Failed to fetch portfolios"}), 500


@crm_bp.route("/portfolios", methods=["POST"])
@require_auth
@limiter.limit("10 per hour")
def create_portfolio():
    """
    Create new portfolio

    Request Body:
        {
            "name": "Rental Properties",
            "description": "Nashville rental portfolio",
            "targetReturn": 8.5
        }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Request body is required"}), 400

        if not data.get("name"):
            return jsonify({"error": "name is required"}), 400

        with get_db_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO user_portfolios (user_id, name, description, target_return)
                VALUES (%s, %s, %s, %s)
                RETURNING id, name, description, target_return, created_at, updated_at
            """, (
                g.user_id,
                data["name"],
                data.get("description"),
                data.get("targetReturn")
            ))

            result = cursor.fetchone()

            logger.info(f"Portfolio created: {result[0]} for user {g.user_id}")

            return jsonify({
                "id": str(result[0]),
                "name": result[1],
                "description": result[2],
                "targetReturn": float(result[3]) if result[3] else None,
                "createdAt": result[4].isoformat(),
                "updatedAt": result[5].isoformat(),
                "propertyCount": 0,
                "totalValue": 0,
                "monthlyCashFlow": 0
            }), 201

    except psycopg2.errors.UniqueViolation:
        return jsonify({"error": "A portfolio with this name already exists"}), 409
    except Exception as e:
        logger.error(f"Create portfolio error: {e}", exc_info=True)
        return jsonify({"error": "Failed to create portfolio"}), 500


@crm_bp.route("/portfolios/<portfolio_id>", methods=["GET"])
@require_auth
@limiter.limit("60 per minute")
def get_portfolio(portfolio_id):
    """Get single portfolio with all properties"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Get portfolio
            cursor.execute("""
                SELECT id, name, description, target_return, created_at, updated_at
                FROM user_portfolios
                WHERE id = %s AND user_id = %s
            """, (portfolio_id, g.user_id))

            row = cursor.fetchone()

            if not row:
                return jsonify({"error": "Portfolio not found"}), 404

            portfolio = {
                "id": str(row[0]),
                "name": row[1],
                "description": row[2],
                "targetReturn": float(row[3]) if row[3] else None,
                "createdAt": row[4].isoformat(),
                "updatedAt": row[5].isoformat()
            }

            # Get properties
            cursor.execute("""
                SELECT id, zpid, purchase_price, purchase_date, current_value,
                       monthly_rent, monthly_expenses, is_vacant, lease_end_date,
                       notes, created_at, updated_at
                FROM portfolio_properties
                WHERE portfolio_id = %s
                ORDER BY created_at DESC
            """, (portfolio_id,))

            properties = []
            total_value = 0
            total_rent = 0
            total_expenses = 0
            vacant_count = 0

            for prop in cursor.fetchall():
                p = {
                    "id": str(prop[0]),
                    "zpid": prop[1],
                    "purchasePrice": float(prop[2]) if prop[2] else None,
                    "purchaseDate": prop[3].isoformat() if prop[3] else None,
                    "currentValue": float(prop[4]) if prop[4] else None,
                    "monthlyRent": float(prop[5]) if prop[5] else None,
                    "monthlyExpenses": float(prop[6]) if prop[6] else None,
                    "isVacant": prop[7],
                    "leaseEndDate": prop[8].isoformat() if prop[8] else None,
                    "notes": prop[9],
                    "createdAt": prop[10].isoformat(),
                    "updatedAt": prop[11].isoformat()
                }
                properties.append(p)

                if prop[4]:
                    total_value += float(prop[4])
                if prop[5]:
                    total_rent += float(prop[5])
                if prop[6]:
                    total_expenses += float(prop[6])
                if prop[7]:
                    vacant_count += 1

            portfolio["properties"] = properties
            portfolio["propertyCount"] = len(properties)
            portfolio["totalValue"] = total_value
            portfolio["totalRent"] = total_rent
            portfolio["totalExpenses"] = total_expenses
            portfolio["monthlyCashFlow"] = total_rent - total_expenses
            portfolio["vacantCount"] = vacant_count

            return jsonify(portfolio), 200

    except Exception as e:
        logger.error(f"Get portfolio error: {e}", exc_info=True)
        return jsonify({"error": "Failed to fetch portfolio"}), 500


@crm_bp.route("/portfolios/<portfolio_id>", methods=["PUT"])
@require_auth
@limiter.limit("20 per hour")
def update_portfolio(portfolio_id):
    """Update portfolio name, description, or target return"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Request body is required"}), 400

        with get_db_connection() as conn:
            cursor = conn.cursor()

            updates = []
            params = []

            if "name" in data:
                updates.append("name = %s")
                params.append(data["name"])

            if "description" in data:
                updates.append("description = %s")
                params.append(data["description"])

            if "targetReturn" in data:
                updates.append("target_return = %s")
                params.append(data["targetReturn"])

            if not updates:
                return jsonify({"error": "No fields to update"}), 400

            params.extend([portfolio_id, g.user_id])

            cursor.execute(f"""
                UPDATE user_portfolios
                SET {', '.join(updates)}
                WHERE id = %s AND user_id = %s
                RETURNING id, name, description, target_return, updated_at
            """, params)

            result = cursor.fetchone()

            if not result:
                return jsonify({"error": "Portfolio not found"}), 404

            return jsonify({
                "id": str(result[0]),
                "name": result[1],
                "description": result[2],
                "targetReturn": float(result[3]) if result[3] else None,
                "updatedAt": result[4].isoformat()
            }), 200

    except psycopg2.errors.UniqueViolation:
        return jsonify({"error": "A portfolio with this name already exists"}), 409
    except Exception as e:
        logger.error(f"Update portfolio error: {e}", exc_info=True)
        return jsonify({"error": "Failed to update portfolio"}), 500


@crm_bp.route("/portfolios/<portfolio_id>", methods=["DELETE"])
@require_auth
@limiter.limit("10 per hour")
def delete_portfolio(portfolio_id):
    """Delete portfolio (cascade deletes properties)"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                DELETE FROM user_portfolios
                WHERE id = %s AND user_id = %s
                RETURNING id
            """, (portfolio_id, g.user_id))

            if not cursor.fetchone():
                return jsonify({"error": "Portfolio not found"}), 404

            return jsonify({"message": "Portfolio deleted successfully"}), 200

    except Exception as e:
        logger.error(f"Delete portfolio error: {e}", exc_info=True)
        return jsonify({"error": "Failed to delete portfolio"}), 500


# ============================================================================
# PORTFOLIO PROPERTIES ENDPOINTS
# ============================================================================

@crm_bp.route("/portfolios/<portfolio_id>/properties", methods=["POST"])
@require_auth
@limiter.limit("30 per hour")
def add_portfolio_property(portfolio_id):
    """
    Add property to portfolio

    Request Body:
        {
            "zpid": "12345",
            "purchasePrice": 250000,
            "purchaseDate": "2024-01-15",
            "currentValue": 260000,
            "monthlyRent": 2000,
            "monthlyExpenses": 500,
            "isVacant": false,
            "leaseEndDate": "2025-01-15",
            "notes": "Great property"
        }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Request body is required"}), 400

        if not data.get("zpid"):
            return jsonify({"error": "zpid is required"}), 400

        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Verify portfolio ownership
            cursor.execute("""
                SELECT id FROM user_portfolios
                WHERE id = %s AND user_id = %s
            """, (portfolio_id, g.user_id))

            if not cursor.fetchone():
                return jsonify({"error": "Portfolio not found"}), 404

            cursor.execute("""
                INSERT INTO portfolio_properties
                (portfolio_id, zpid, purchase_price, purchase_date, current_value,
                 monthly_rent, monthly_expenses, is_vacant, lease_end_date, notes)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id, zpid, purchase_price, purchase_date, current_value,
                          monthly_rent, monthly_expenses, is_vacant, lease_end_date,
                          notes, created_at
            """, (
                portfolio_id,
                data["zpid"],
                data.get("purchasePrice"),
                data.get("purchaseDate"),
                data.get("currentValue"),
                data.get("monthlyRent"),
                data.get("monthlyExpenses"),
                data.get("isVacant", False),
                data.get("leaseEndDate"),
                data.get("notes")
            ))

            result = cursor.fetchone()

            logger.info(f"Property {data['zpid']} added to portfolio {portfolio_id}")

            return jsonify({
                "id": str(result[0]),
                "portfolioId": portfolio_id,
                "zpid": result[1],
                "purchasePrice": float(result[2]) if result[2] else None,
                "purchaseDate": result[3].isoformat() if result[3] else None,
                "currentValue": float(result[4]) if result[4] else None,
                "monthlyRent": float(result[5]) if result[5] else None,
                "monthlyExpenses": float(result[6]) if result[6] else None,
                "isVacant": result[7],
                "leaseEndDate": result[8].isoformat() if result[8] else None,
                "notes": result[9],
                "createdAt": result[10].isoformat()
            }), 201

    except psycopg2.errors.UniqueViolation:
        return jsonify({"error": "Property already in this portfolio"}), 409
    except Exception as e:
        logger.error(f"Add portfolio property error: {e}", exc_info=True)
        return jsonify({"error": "Failed to add property"}), 500


@crm_bp.route("/portfolios/<portfolio_id>/properties/<property_id>", methods=["PUT"])
@require_auth
@limiter.limit("30 per hour")
def update_portfolio_property(portfolio_id, property_id):
    """Update property in portfolio"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Request body is required"}), 400

        with get_db_connection() as conn:
            cursor = conn.cursor()

            updates = []
            params = []

            field_mapping = {
                "purchasePrice": "purchase_price",
                "purchaseDate": "purchase_date",
                "currentValue": "current_value",
                "monthlyRent": "monthly_rent",
                "monthlyExpenses": "monthly_expenses",
                "isVacant": "is_vacant",
                "leaseEndDate": "lease_end_date",
                "notes": "notes"
            }

            for js_field, db_field in field_mapping.items():
                if js_field in data:
                    updates.append(f"{db_field} = %s")
                    params.append(data[js_field])

            if not updates:
                return jsonify({"error": "No fields to update"}), 400

            params.extend([property_id, portfolio_id, g.user_id])

            cursor.execute(f"""
                UPDATE portfolio_properties
                SET {', '.join(updates)}
                WHERE id = %s AND portfolio_id = %s
                AND portfolio_id IN (SELECT id FROM user_portfolios WHERE user_id = %s)
                RETURNING id, zpid, purchase_price, current_value,
                          monthly_rent, monthly_expenses, is_vacant, updated_at
            """, params)

            result = cursor.fetchone()

            if not result:
                return jsonify({"error": "Property not found"}), 404

            return jsonify({
                "id": str(result[0]),
                "zpid": result[1],
                "purchasePrice": float(result[2]) if result[2] else None,
                "currentValue": float(result[3]) if result[3] else None,
                "monthlyRent": float(result[4]) if result[4] else None,
                "monthlyExpenses": float(result[5]) if result[5] else None,
                "isVacant": result[6],
                "updatedAt": result[7].isoformat()
            }), 200

    except Exception as e:
        logger.error(f"Update portfolio property error: {e}", exc_info=True)
        return jsonify({"error": "Failed to update property"}), 500


@crm_bp.route("/portfolios/<portfolio_id>/properties/<property_id>", methods=["DELETE"])
@require_auth
@limiter.limit("20 per hour")
def remove_portfolio_property(portfolio_id, property_id):
    """Remove property from portfolio"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                DELETE FROM portfolio_properties
                WHERE id = %s AND portfolio_id = %s
                AND portfolio_id IN (SELECT id FROM user_portfolios WHERE user_id = %s)
                RETURNING id
            """, (property_id, portfolio_id, g.user_id))

            if not cursor.fetchone():
                return jsonify({"error": "Property not found"}), 404

            return jsonify({"message": "Property removed from portfolio"}), 200

    except Exception as e:
        logger.error(f"Remove portfolio property error: {e}", exc_info=True)
        return jsonify({"error": "Failed to remove property"}), 500
