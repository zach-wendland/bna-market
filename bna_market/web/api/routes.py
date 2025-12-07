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


def get_app_db_connection():
    """Get database connection using Flask app config for database path"""
    db_path = current_app.config.get("DATABASE_PATH")
    return get_db_connection(db_path)

# Explicit table name mapping to prevent SQL injection
PROPERTY_TYPE_TABLE_MAP = {
    "forsale": "BNA_FORSALE",
    "rental": "BNA_RENTALS"
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
                FROM BNA_RENTALS
                WHERE price IS NOT NULL AND price > 0
            """)
            rental_stats = cursor.fetchone()
            rental_count = rental_stats[0] if rental_stats else 0
            rental_avg = round(rental_stats[1]) if rental_stats and rental_stats[1] else None

            cursor.execute("""
                SELECT COUNT(*) as count, AVG(price) as avg_price
                FROM BNA_FORSALE
                WHERE price IS NOT NULL AND price > 0
            """)
            forsale_stats = cursor.fetchone()
            forsale_count = forsale_stats[0] if forsale_stats else 0
            forsale_avg = round(forsale_stats[1]) if forsale_stats and forsale_stats[1] else None

            # Get rental properties (limited for display)
            cursor.execute("""
                SELECT zpid, address, price, bedrooms, bathrooms, livingArea,
                       propertyType, latitude, longitude, imgSrc, detailUrl,
                       daysOnZillow, listingStatus
                FROM BNA_RENTALS
                ORDER BY price DESC
                LIMIT 100
            """)
            columns = [desc[0] for desc in cursor.description]
            rentals = []
            for row in cursor.fetchall():
                prop = dict(zip(columns, row))
                prop['detailUrl'] = fix_zillow_url(prop.get('detailUrl'))
                if prop.get('price') and prop.get('livingArea') and prop['livingArea'] > 0:
                    prop['pricePerSqft'] = round(prop['price'] / prop['livingArea'], 2)
                else:
                    prop['pricePerSqft'] = None
                rentals.append(prop)

            # Get for-sale properties (limited for display)
            cursor.execute("""
                SELECT zpid, address, price, bedrooms, bathrooms, livingArea,
                       propertyType, latitude, longitude, imgSrc, detailUrl,
                       daysOnZillow, listingStatus
                FROM BNA_FORSALE
                ORDER BY price DESC
                LIMIT 100
            """)
            columns = [desc[0] for desc in cursor.description]
            forsale = []
            for row in cursor.fetchall():
                prop = dict(zip(columns, row))
                prop['detailUrl'] = fix_zillow_url(prop.get('detailUrl'))
                if prop.get('price') and prop.get('livingArea') and prop['livingArea'] > 0:
                    prop['pricePerSqft'] = round(prop['price'] / prop['livingArea'], 2)
                else:
                    prop['pricePerSqft'] = None
                forsale.append(prop)

            # Get FRED metrics
            cursor.execute("""
                SELECT date, metric_name as metricName, series_id as seriesId, value
                FROM BNA_FRED_METRICS
                ORDER BY date DESC
            """)
            columns = [desc[0] for desc in cursor.description]
            fred_metrics = [dict(zip(columns, row)) for row in cursor.fetchall()]

            # Calculate FRED KPIs (latest values)
            fred_kpis = {}
            metric_map = {
                'median_price': 'medianPrice',
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

        import os
        from datetime import datetime

        # Get database last modified time
        db_path = os.environ.get("DATABASE_PATH", "BNASFR02.DB")
        try:
            mtime = os.path.getmtime(db_path)
            last_updated = datetime.fromtimestamp(mtime).isoformat() + "Z"
        except (OSError, FileNotFoundError, ValueError):
            last_updated = None

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

        # Build WHERE clause with filters
        conditions = []
        params = []

        # Price filters
        if request.args.get("min_price"):
            conditions.append("price >= ?")
            params.append(float(request.args.get("min_price")))
        if request.args.get("max_price"):
            conditions.append("price <= ?")
            params.append(float(request.args.get("max_price")))

        # Bedroom filters
        if request.args.get("min_beds"):
            conditions.append("bedrooms >= ?")
            params.append(int(request.args.get("min_beds")))
        if request.args.get("max_beds"):
            conditions.append("bedrooms <= ?")
            params.append(int(request.args.get("max_beds")))

        # Bathroom filters
        if request.args.get("min_baths"):
            conditions.append("bathrooms >= ?")
            params.append(float(request.args.get("min_baths")))
        if request.args.get("max_baths"):
            conditions.append("bathrooms <= ?")
            params.append(float(request.args.get("max_baths")))

        # Square footage filters
        if request.args.get("min_sqft"):
            conditions.append("livingArea >= ?")
            params.append(int(request.args.get("min_sqft")))
        if request.args.get("max_sqft"):
            conditions.append("livingArea <= ?")
            params.append(int(request.args.get("max_sqft")))

        # City filter (partial match, case-insensitive)
        if request.args.get("city"):
            conditions.append("LOWER(address) LIKE ?")
            params.append(f'%{request.args.get("city").lower()}%')

        # ZIP code filter (exact match)
        if request.args.get("zip_code"):
            conditions.append("address LIKE ?")
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
                SELECT zpid, address, price, bedrooms, bathrooms, livingArea,
                       propertyType, latitude, longitude, imgSrc, detailUrl,
                       daysOnZillow, listingStatus
                FROM {table_name}
                WHERE {where_clause}
                ORDER BY price DESC
                LIMIT ? OFFSET ?
            """
            cursor.execute(data_query, params + [per_page, offset])

            # Fetch results and convert to list of dicts
            columns = [desc[0] for desc in cursor.description]
            properties = []
            for row in cursor.fetchall():
                prop = dict(zip(columns, row))
                # Fix Zillow URL
                prop['detailUrl'] = fix_zillow_url(prop.get('detailUrl'))
                # Calculate price per square foot
                if prop.get('price') and prop.get('livingArea') and prop['livingArea'] > 0:
                    prop['pricePerSqft'] = round(prop['price'] / prop['livingArea'], 2)
                else:
                    prop['pricePerSqft'] = None
                properties.append(prop)

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

        # Build WHERE clause with same filters as search
        conditions = []
        params = []

        # Price filters
        if request.args.get("min_price"):
            conditions.append("price >= ?")
            params.append(float(request.args.get("min_price")))
        if request.args.get("max_price"):
            conditions.append("price <= ?")
            params.append(float(request.args.get("max_price")))

        # Bedroom filters
        if request.args.get("min_beds"):
            conditions.append("bedrooms >= ?")
            params.append(int(request.args.get("min_beds")))
        if request.args.get("max_beds"):
            conditions.append("bedrooms <= ?")
            params.append(int(request.args.get("max_beds")))

        # Bathroom filters
        if request.args.get("min_baths"):
            conditions.append("bathrooms >= ?")
            params.append(float(request.args.get("min_baths")))
        if request.args.get("max_baths"):
            conditions.append("bathrooms <= ?")
            params.append(float(request.args.get("max_baths")))

        # Square footage filters
        if request.args.get("min_sqft"):
            conditions.append("livingArea >= ?")
            params.append(int(request.args.get("min_sqft")))
        if request.args.get("max_sqft"):
            conditions.append("livingArea <= ?")
            params.append(int(request.args.get("max_sqft")))

        # City filter
        if request.args.get("city"):
            conditions.append("LOWER(address) LIKE ?")
            params.append(f'%{request.args.get("city").lower()}%')

        # ZIP code filter
        if request.args.get("zip_code"):
            conditions.append("address LIKE ?")
            params.append(f'%{request.args.get("zip_code")}%')

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        # Execute query
        with get_app_db_connection() as conn:
            cursor = conn.cursor()

            query = f"""
                SELECT zpid, address, price, bedrooms, bathrooms, livingArea,
                       propertyType, latitude, longitude, daysOnZillow,
                       listingStatus, detailUrl
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
        # Build WHERE clause with filters
        conditions = []
        params = []

        # Metric name filter
        if request.args.get("metric_name"):
            conditions.append("metric_name = ?")
            params.append(request.args.get("metric_name"))

        # Series ID filter
        if request.args.get("series_id"):
            conditions.append("series_id = ?")
            params.append(request.args.get("series_id"))

        # Date range filters
        if request.args.get("start_date"):
            conditions.append("date >= ?")
            params.append(request.args.get("start_date"))
        if request.args.get("end_date"):
            conditions.append("date <= ?")
            params.append(request.args.get("end_date"))

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        # Execute query
        with get_app_db_connection() as conn:
            cursor = conn.cursor()

            query = f"""
                SELECT date, metric_name, series_id, value
                FROM BNA_FRED_METRICS
                WHERE {where_clause}
                ORDER BY date DESC, metric_name
            """
            cursor.execute(query, params)

            # Fetch results and convert to list of dicts
            columns = [desc[0] for desc in cursor.description]
            metrics = []
            for row in cursor.fetchall():
                metrics.append(dict(zip(columns, row)))

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
    return jsonify(
        {
            "status": "healthy",
            "api_version": "1.0",
            "endpoints": [
                "/api/dashboard",
                "/api/properties/search",
                "/api/properties/export",
                "/api/metrics/fred",
                "/api/health",
            ],
        }
    )
