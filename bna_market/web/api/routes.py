"""
API Routes for BNA Market Application

Endpoints:
- /api/properties/search - Search properties with filters and pagination
- /api/properties/export - Export filtered properties as CSV
- /api/metrics/fred - Get FRED economic metrics with optional filters
"""

from flask import request, jsonify, make_response, current_app
from io import StringIO
import csv

from bna_market.web.api import api_bp
from bna_market.web.app import limiter
from bna_market.utils.database import get_db_connection
from bna_market.utils.logger import setup_logger

logger = setup_logger("api")


def snake_to_camel(name: str) -> str:
    """Convert snake_case to camelCase for JSON API responses"""
    components = name.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])


# Fields that should be numeric (not strings)
NUMERIC_FIELDS = {
    'price', 'bathrooms', 'living_area', 'latitude', 'longitude',
    'price_per_sqft', 'bedrooms', 'days_on_zillow'
}


def convert_numerics(prop: dict) -> dict:
    """Convert Decimal/string numeric values to proper Python floats/ints"""
    from decimal import Decimal
    result = {}
    for k, v in prop.items():
        if k in NUMERIC_FIELDS and v is not None:
            if isinstance(v, Decimal):
                # Convert Decimal to float or int
                result[k] = float(v) if '.' in str(v) else int(v)
            elif isinstance(v, str):
                # Convert string numbers to float or int
                try:
                    result[k] = float(v) if '.' in v else int(v)
                except (ValueError, TypeError):
                    result[k] = v
            else:
                result[k] = v
        else:
            result[k] = v
    return result


def transform_property(prop: dict) -> dict:
    """Transform property dict: convert numerics and snake_case to camelCase"""
    converted = convert_numerics(prop)
    return {snake_to_camel(k): v for k, v in converted.items()}


def get_app_db_connection():
    """Get database connection (Supabase PostgreSQL)"""
    return get_db_connection()


# Explicit table name mapping to prevent SQL injection (lowercase for PostgreSQL)
PROPERTY_TYPE_TABLE_MAP = {
    "forsale": "bna_forsale",
    "rental": "bna_rentals"
}


def fix_zillow_url(detail_url):
    """Fix Zillow URLs stored as relative paths"""
    if not detail_url:
        return None
    if detail_url.startswith("http"):
        return detail_url
    return f"https://www.zillow.com{detail_url}"


@api_bp.route("/dashboard", methods=["GET"])
@limiter.limit("30 per minute")
def get_dashboard():
    """
    Get all dashboard data in one call for Vue frontend

    Returns:
        JSON with propertyKPIs, fredKPIs, rentals, forsale, fredMetrics, lastUpdated
    """
    try:
        with get_app_db_connection() as conn:
            cursor = conn.cursor()

            # Get KPI aggregates from FULL database
            cursor.execute("""
                SELECT COUNT(*) as count, AVG(price) as avg_price
                FROM bna_rentals
                WHERE price IS NOT NULL AND price > 0
            """)
            rental_stats = cursor.fetchone()
            rental_count = rental_stats[0] if rental_stats else 0
            rental_avg = round(rental_stats[1]) if rental_stats and rental_stats[1] else None

            cursor.execute("""
                SELECT COUNT(*) as count, AVG(price) as avg_price
                FROM bna_forsale
                WHERE price IS NOT NULL AND price > 0
            """)
            forsale_stats = cursor.fetchone()
            forsale_count = forsale_stats[0] if forsale_stats else 0
            forsale_avg = round(forsale_stats[1]) if forsale_stats and forsale_stats[1] else None

            # Get rental properties
            cursor.execute("""
                SELECT zpid, address, price, bedrooms, bathrooms, living_area,
                       property_type, latitude, longitude, img_src, detail_url,
                       days_on_zillow, listing_status
                FROM bna_rentals
                ORDER BY price DESC
            """)
            columns = [desc[0] for desc in cursor.description]
            rentals = []
            for row in cursor.fetchall():
                prop = dict(zip(columns, row))
                prop['detail_url'] = fix_zillow_url(prop.get('detail_url'))
                if prop.get('price') and prop.get('living_area') and prop['living_area'] > 0:
                    prop['price_per_sqft'] = round(prop['price'] / prop['living_area'], 2)
                else:
                    prop['price_per_sqft'] = None
                rentals.append(transform_property(prop))

            # Get for-sale properties
            cursor.execute("""
                SELECT zpid, address, price, bedrooms, bathrooms, living_area,
                       property_type, latitude, longitude, img_src, detail_url,
                       days_on_zillow, listing_status
                FROM bna_forsale
                ORDER BY price DESC
            """)
            columns = [desc[0] for desc in cursor.description]
            forsale = []
            for row in cursor.fetchall():
                prop = dict(zip(columns, row))
                prop['detail_url'] = fix_zillow_url(prop.get('detail_url'))
                if prop.get('price') and prop.get('living_area') and prop['living_area'] > 0:
                    prop['price_per_sqft'] = round(prop['price'] / prop['living_area'], 2)
                else:
                    prop['price_per_sqft'] = None
                forsale.append(transform_property(prop))

            # Get FRED metrics
            cursor.execute("""
                SELECT date, metric_name as "metricName", series_id as "seriesId", value
                FROM bna_fred_metrics
                ORDER BY date DESC
            """)
            columns = [desc[0] for desc in cursor.description]
            fred_metrics = []
            for row in cursor.fetchall():
                metric = dict(zip(columns, row))
                # Convert date to ISO format for Chart.js compatibility
                if metric.get('date') and hasattr(metric['date'], 'isoformat'):
                    metric['date'] = metric['date'].isoformat()
                fred_metrics.append(metric)

            # Calculate FRED KPIs (latest values)
            fred_kpis = {}
            metric_map = {
                'median_listing_price_change': 'medianPrice',
                'active_listings': 'activeListings',
                'median_dom': 'medianDaysOnMarket',
                'msa_per_capita_income': 'perCapitaIncome'
            }

            latest_by_metric = {}
            for metric in fred_metrics:
                name = metric.get('metricName')
                if name not in latest_by_metric:
                    latest_by_metric[name] = metric

            for db_name, kpi_name in metric_map.items():
                if db_name in latest_by_metric:
                    fred_kpis[kpi_name] = latest_by_metric[db_name].get('value')

        from datetime import datetime

        # For Supabase, we don't have a local file timestamp
        # Use current time as a placeholder or query for latest update
        last_updated = datetime.utcnow().isoformat() + "Z"

        return jsonify({
            "propertyKPIs": {
                "totalRentalListings": rental_count,
                "avgRentalPrice": rental_avg,
                "totalForSaleListings": forsale_count,
                "avgSalePrice": forsale_avg
            },
            "fredKPIs": fred_kpis,
            "rentals": rentals,
            "forsale": forsale,
            "fredMetrics": fred_metrics,
            "lastUpdated": last_updated
        })

    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        return jsonify({"error": "Internal server error"}), 500


@api_bp.route("/properties/search", methods=["GET"])
@limiter.limit("60 per minute")
def search_properties():
    """
    Search properties with filters and pagination

    Query Parameters:
        property_type (str): 'forsale' or 'rental' (required)
        min_price (float): Minimum price
        max_price (float): Maximum price
        min_beds (int): Minimum bedrooms
        max_beds (int): Maximum bedrooms
        min_baths (int): Minimum bathrooms
        max_baths (int): Maximum bathrooms
        min_sqft (int): Minimum square footage
        max_sqft (int): Maximum square footage
        city (str): City name (partial match)
        zip_code (str): ZIP code (exact match)
        page (int): Page number (default: 1)
        per_page (int): Items per page (default: 20, max: 100)

    Returns:
        JSON response with properties array, pagination info, and total count
    """
    try:
        # Validate required parameter
        property_type = request.args.get("property_type", "").lower()
        if property_type not in PROPERTY_TYPE_TABLE_MAP:
            return jsonify({"error": 'property_type must be either "forsale" or "rental"'}), 400

        # Get table name from secure mapping
        table_name = PROPERTY_TYPE_TABLE_MAP[property_type]

        # Get pagination parameters
        page = max(1, int(request.args.get("page", 1)))
        per_page = min(100, max(1, int(request.args.get("per_page", 20))))
        offset = (page - 1) * per_page

        # Build WHERE clause with filters (PostgreSQL uses %s placeholders)
        conditions = []
        params = []

        # Price filters
        if request.args.get("min_price"):
            conditions.append("price >= %s")
            params.append(float(request.args.get("min_price")))
        if request.args.get("max_price"):
            conditions.append("price <= %s")
            params.append(float(request.args.get("max_price")))

        # Bedroom filters
        if request.args.get("min_beds"):
            conditions.append("bedrooms >= %s")
            params.append(int(request.args.get("min_beds")))
        if request.args.get("max_beds"):
            conditions.append("bedrooms <= %s")
            params.append(int(request.args.get("max_beds")))

        # Bathroom filters
        if request.args.get("min_baths"):
            conditions.append("bathrooms >= %s")
            params.append(float(request.args.get("min_baths")))
        if request.args.get("max_baths"):
            conditions.append("bathrooms <= %s")
            params.append(float(request.args.get("max_baths")))

        # Square footage filters
        if request.args.get("min_sqft"):
            conditions.append('living_area >= %s')
            params.append(int(request.args.get("min_sqft")))
        if request.args.get("max_sqft"):
            conditions.append('living_area <= %s')
            params.append(int(request.args.get("max_sqft")))

        # City filter (partial match, case-insensitive)
        if request.args.get("city"):
            conditions.append("LOWER(address) LIKE %s")
            params.append(f'%{request.args.get("city").lower()}%')

        # ZIP code filter (exact match)
        if request.args.get("zip_code"):
            conditions.append("address LIKE %s")
            params.append(f'%{request.args.get("zip_code")}%')

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        # Execute queries with database connection
        with get_app_db_connection() as conn:
            cursor = conn.cursor()

            # Get total count
            count_query = f"SELECT COUNT(*) FROM {table_name} WHERE {where_clause}"
            cursor.execute(count_query, params)
            total_count = cursor.fetchone()[0]

            # Get paginated results
            data_query = f"""
                SELECT zpid, address, price, bedrooms, bathrooms, living_area,
                       property_type, latitude, longitude, img_src, detail_url,
                       days_on_zillow, listing_status
                FROM {table_name}
                WHERE {where_clause}
                ORDER BY price DESC
                LIMIT %s OFFSET %s
            """
            cursor.execute(data_query, params + [per_page, offset])

            # Fetch results and convert to list of dicts
            columns = [desc[0] for desc in cursor.description]
            properties = []
            for row in cursor.fetchall():
                prop = dict(zip(columns, row))
                # Fix Zillow URL
                prop['detail_url'] = fix_zillow_url(prop.get('detail_url'))
                # Calculate price per square foot
                if prop.get('price') and prop.get('living_area') and prop['living_area'] > 0:
                    prop['price_per_sqft'] = round(prop['price'] / prop['living_area'], 2)
                else:
                    prop['price_per_sqft'] = None
                properties.append(transform_property(prop))

        # Calculate pagination metadata
        total_pages = (total_count + per_page - 1) // per_page

        logger.info(
            f"Search executed: {property_type}, page {page}, found {total_count} total results"
        )

        return jsonify(
            {
                "properties": properties,
                "pagination": {
                    "page": page,
                    "perPage": per_page,
                    "totalCount": total_count,
                    "totalPages": total_pages,
                    "hasNext": page < total_pages,
                    "hasPrev": page > 1,
                },
            }
        )

    except ValueError as e:
        logger.error(f"Invalid parameter value: {e}")
        return jsonify({"error": f"Invalid parameter value: {str(e)}"}), 400
    except Exception as e:
        logger.error(f"Search error: {e}")
        return jsonify({"error": "Internal server error"}), 500


@api_bp.route("/properties/export", methods=["GET"])
@limiter.limit("10 per minute")
def export_properties():
    """
    Export filtered properties as CSV file

    Query Parameters:
        Same as /api/properties/search (excluding pagination)
        property_type (str): 'forsale' or 'rental' (required)

    Returns:
        CSV file download with filtered properties
    """
    try:
        # Validate required parameter
        property_type = request.args.get("property_type", "").lower()
        if property_type not in PROPERTY_TYPE_TABLE_MAP:
            return jsonify({"error": 'property_type must be either "forsale" or "rental"'}), 400

        # Get table name from secure mapping
        table_name = PROPERTY_TYPE_TABLE_MAP[property_type]

        # Build WHERE clause with same filters as search (PostgreSQL %s placeholders)
        conditions = []
        params = []

        # Price filters
        if request.args.get("min_price"):
            conditions.append("price >= %s")
            params.append(float(request.args.get("min_price")))
        if request.args.get("max_price"):
            conditions.append("price <= %s")
            params.append(float(request.args.get("max_price")))

        # Bedroom filters
        if request.args.get("min_beds"):
            conditions.append("bedrooms >= %s")
            params.append(int(request.args.get("min_beds")))
        if request.args.get("max_beds"):
            conditions.append("bedrooms <= %s")
            params.append(int(request.args.get("max_beds")))

        # Bathroom filters
        if request.args.get("min_baths"):
            conditions.append("bathrooms >= %s")
            params.append(float(request.args.get("min_baths")))
        if request.args.get("max_baths"):
            conditions.append("bathrooms <= %s")
            params.append(float(request.args.get("max_baths")))

        # Square footage filters
        if request.args.get("min_sqft"):
            conditions.append('living_area >= %s')
            params.append(int(request.args.get("min_sqft")))
        if request.args.get("max_sqft"):
            conditions.append('living_area <= %s')
            params.append(int(request.args.get("max_sqft")))

        # City filter
        if request.args.get("city"):
            conditions.append("LOWER(address) LIKE %s")
            params.append(f'%{request.args.get("city").lower()}%')

        # ZIP code filter
        if request.args.get("zip_code"):
            conditions.append("address LIKE %s")
            params.append(f'%{request.args.get("zip_code")}%')

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        # Execute query
        with get_app_db_connection() as conn:
            cursor = conn.cursor()

            query = f"""
                SELECT zpid, address, price, bedrooms, bathrooms, living_area,
                       property_type, latitude, longitude, days_on_zillow,
                       listing_status, detail_url
                FROM {table_name}
                WHERE {where_clause}
                ORDER BY price DESC
            """
            cursor.execute(query, params)

            # Create CSV in memory
            output = StringIO()
            columns = [desc[0] for desc in cursor.description]
            writer = csv.writer(output)
            writer.writerow(columns)
            writer.writerows(cursor.fetchall())

            # Prepare CSV response
            csv_data = output.getvalue()
            output.close()

        response = make_response(csv_data)
        response.headers["Content-Type"] = "text/csv"
        response.headers["Content-Disposition"] = (
            f"attachment; filename=bna_{property_type}_export.csv"
        )

        logger.info(
            f"CSV export executed: {property_type}, {len(csv_data.splitlines()) - 1} properties"
        )

        return response

    except ValueError as e:
        logger.error(f"Invalid parameter value: {e}")
        return jsonify({"error": f"Invalid parameter value: {str(e)}"}), 400
    except Exception as e:
        logger.error(f"Export error: {e}")
        return jsonify({"error": "Internal server error"}), 500


@api_bp.route("/metrics/fred", methods=["GET"])
@limiter.limit("30 per minute")
def get_fred_metrics():
    """
    Get FRED economic metrics with optional filters

    Query Parameters:
        metric_name (str): Filter by specific metric (optional)
        start_date (str): Start date in YYYY-MM-DD format (optional)
        end_date (str): End date in YYYY-MM-DD format (optional)
        series_id (str): Filter by FRED series ID (optional)

    Returns:
        JSON response with metrics array and count
    """
    try:
        # Build WHERE clause with filters (PostgreSQL %s placeholders)
        conditions = []
        params = []

        # Metric name filter
        if request.args.get("metric_name"):
            conditions.append("metric_name = %s")
            params.append(request.args.get("metric_name"))

        # Series ID filter
        if request.args.get("series_id"):
            conditions.append("series_id = %s")
            params.append(request.args.get("series_id"))

        # Date range filters
        if request.args.get("start_date"):
            conditions.append("date >= %s")
            params.append(request.args.get("start_date"))
        if request.args.get("end_date"):
            conditions.append("date <= %s")
            params.append(request.args.get("end_date"))

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        # Execute query
        with get_app_db_connection() as conn:
            cursor = conn.cursor()

            query = f"""
                SELECT date, metric_name, series_id, value
                FROM bna_fred_metrics
                WHERE {where_clause}
                ORDER BY date DESC, metric_name
            """
            cursor.execute(query, params)

            # Fetch results and convert to list of dicts
            columns = [desc[0] for desc in cursor.description]
            metrics = []
            for row in cursor.fetchall():
                metric = dict(zip(columns, row))
                # Convert date to string if it's a date object
                if metric.get('date') and hasattr(metric['date'], 'isoformat'):
                    metric['date'] = metric['date'].isoformat()
                metrics.append(metric)

        logger.info(f"FRED metrics query executed, found {len(metrics)} records")

        return jsonify({"metrics": metrics, "count": len(metrics)})

    except Exception as e:
        logger.error(f"FRED metrics error: {e}")
        return jsonify({"error": "Internal server error"}), 500


@api_bp.route("/health", methods=["GET"])
def health_check():
    """
    Health check endpoint for API status verification

    Returns:
        JSON response with API status
    """
    # Test database connection
    db_status = "unknown"
    db_error = None
    try:
        with get_app_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            db_status = "connected"
    except Exception as e:
        db_status = "error"
        db_error = str(e)

    return jsonify(
        {
            "status": "healthy" if db_status == "connected" else "degraded",
            "api_version": "1.0",
            "database": "supabase",
            "db_status": db_status,
            "db_error": db_error,
            "endpoints": [
                "/api/dashboard",
                "/api/properties/search",
                "/api/properties/export",
                "/api/metrics/fred",
                "/api/health",
            ],
        }
    )


@api_bp.route("/auth/ping", methods=["GET"])
def auth_ping():
    """Ultra-simple auth test endpoint added directly to routes.py"""
    return jsonify({"status": "ok", "message": "Auth endpoint works!", "location": "routes.py"}), 200


@api_bp.route("/debug/blueprints", methods=["GET"])
def debug_blueprints():
    """
    Debug endpoint to verify blueprint imports work in production

    This endpoint tests if the auth, lists, and searches blueprints
    can be imported successfully in the Vercel serverless environment.
    """
    import traceback

    results = {
        "status": "ok",
        "flask_app_loaded": True,
        "blueprints": {}
    }

    # Test auth blueprint import
    try:
        from bna_market.web.api.auth_routes import auth_bp
        results["blueprints"]["auth"] = {
            "imported": True,
            "name": auth_bp.name,
            "url_prefix": auth_bp.url_prefix,
            "error": None
        }
    except Exception as e:
        results["blueprints"]["auth"] = {
            "imported": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }
        results["status"] = "error"

    # Test lists blueprint import
    try:
        from bna_market.web.api.lists_routes import lists_bp
        results["blueprints"]["lists"] = {
            "imported": True,
            "name": lists_bp.name,
            "url_prefix": lists_bp.url_prefix,
            "error": None
        }
    except Exception as e:
        results["blueprints"]["lists"] = {
            "imported": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }
        results["status"] = "error"

    # Test searches blueprint import
    try:
        from bna_market.web.api.searches_routes import searches_bp
        results["blueprints"]["searches"] = {
            "imported": True,
            "name": searches_bp.name,
            "url_prefix": searches_bp.url_prefix,
            "error": None
        }
    except Exception as e:
        results["blueprints"]["searches"] = {
            "imported": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }
        results["status"] = "error"

    # Test auth middleware import
    try:
        from bna_market.web.auth import require_auth
        results["auth_middleware"] = {
            "imported": True,
            "error": None
        }
    except Exception as e:
        results["auth_middleware"] = {
            "imported": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }
        results["status"] = "error"

    # Check which blueprints are actually registered with Flask app
    try:
        registered_blueprints = list(current_app.blueprints.keys())
        results["registered_blueprints"] = registered_blueprints
        results["total_registered"] = len(registered_blueprints)
    except Exception as e:
        results["registered_blueprints_error"] = str(e)

    return jsonify(results)
