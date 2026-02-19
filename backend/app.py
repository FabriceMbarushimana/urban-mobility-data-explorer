
# URBAN MOBILITY EXPLORER - Flask API Backend

# This Flask application provides RESTful API endpoints for analyzing
# NYC taxi trip data stored in MySQL database.


# Standard library imports
from datetime import timedelta
import sys
import os

# Third-party imports
from flask import Flask, request, jsonify, session
from flask_cors import CORS
from functools import wraps

# Add parent directory to path for custom module imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Custom module imports
from backend.database_operations import DatabaseHandler
from custom_algorithms import CustomSort, OutlierDetector, TripAggregator


# FLASK APPLICATION INITIALIZATION

app = Flask(__name__)
app.secret_key = 'urban-mobility-secret-2026'  # Secret key for session management


# SESSION CONFIGURATION

app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # CSRF protection
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent XSS attacks
app.config['SESSION_COOKIE_NAME'] = 'session'  # Session cookie name
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)  # Session expires after 24 hours


# CORS (Cross-Origin Resource Sharing) CONFIGURATION

# Allow frontend running on port 5500 to access this API on port 5000
CORS(
    app,
    supports_credentials=True,  # Allow cookies and credentials
    origins=[
        'http://127.0.0.1:5500',  # Local development server
        'http://localhost:5500',   # Alternative localhost address
     ]
)


# DATABASE HANDLER INITIALIZATION

# Initialize database connection handler for MySQL operations
db_handler = DatabaseHandler()


# API ENDPOINTS - STATISTICS

# Authentication has been removed - all endpoints are publicly accessible

@app.route('/api/stats/summary', methods=['GET'])
def get_summary():
    """
    Get overall dataset summary statistics
    
    Returns:
        JSON: Summary statistics including total trips, avg fare, avg distance, etc.
    """
    try:
        summary = db_handler.get_summary_stats()
        return jsonify(summary)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# API ENDPOINTS - TRIPS DATA

@app.route('/api/trips/list', methods=['GET'])
def get_trips():
    """
    Get trips with optional filtering and pagination
    
    Query Parameters:
        limit (int): Number of records to return (default: 100)
        offset (int): Number of records to skip (default: 0)
        borough (str): Filter by NYC borough
        min_fare, max_fare (float): Fare amount range
        min_distance, max_distance (float): Trip distance range
        start_date, end_date (str): Date range filter
        hour (int): Filter by hour of day (0-23)
        is_weekend (bool): Filter weekend/weekday trips
    
    Returns:
        JSON: List of trip records matching filters
    """
    try:
        # Parse query parameters with default values
        limit = int(request.args.get('limit', 100))
        offset = int(request.args.get('offset', 0))
        borough = request.args.get('borough', None)
        min_fare = request.args.get('min_fare', None)
        max_fare = request.args.get('max_fare', None)
        min_distance = request.args.get('min_distance', None)
        max_distance = request.args.get('max_distance', None)
        start_date = request.args.get('start_date', None)
        end_date = request.args.get('end_date', None)
        hour = request.args.get('hour', None)
        is_weekend = request.args.get('is_weekend', None)

        trips = db_handler.get_trips(
            limit=limit,
            offset=offset,
            borough=borough,
            min_fare=min_fare,
            max_fare=max_fare,
            min_distance=min_distance,
            max_distance=max_distance,
            start_date=start_date,
            end_date=end_date,
            hour=hour,
            is_weekend=is_weekend
        )

        return jsonify({'trips': trips})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# API ENDPOINTS - ANALYSIS


@app.route('/api/analysis/hourly-patterns', methods=['GET'])
def get_hourly_patterns():
    """
    Get trip patterns aggregated by hour of day
    
    Returns:
        JSON: Hourly statistics including trip counts, avg fare, avg distance
    """
    try:
        patterns = db_handler.get_hourly_patterns()
        return jsonify(patterns)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analysis/borough', methods=['GET'])
def get_borough_analysis():
    """
    Get analysis grouped by NYC borough (Manhattan, Brooklyn, Queens, Bronx, Staten Island)
    
    Returns:
        JSON: Borough-level statistics for pickup and dropoff locations
    """
    try:
        analysis = db_handler.get_borough_analysis()
        return jsonify(analysis)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analysis/fare-distribution', methods=['GET'])
def get_fare_distribution():
    """
    Get fare amount distribution across different price ranges
    
    Returns:
        JSON: Distribution of trips by fare brackets
    """
    try:
        distribution = db_handler.get_fare_distribution()
        return jsonify(distribution)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analysis/distance', methods=['GET'])
def get_distance_analysis():
    """
    Get distance-based insights and patterns
    
    Returns:
        JSON: Statistics about trip distances, averages, and distributions
    """
    try:
        analysis = db_handler.get_distance_analysis()
        return jsonify(analysis)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# API ENDPOINTS - ROUTES


@app.route('/api/routes/top', methods=['GET'])
def get_top_routes():
    """
    Get most popular routes using custom sorting algorithm
    
    Query Parameters:
        limit (int): Number of top routes to return (default: 10)
    
    Returns:
        JSON: List of most frequent pickup-dropoff location pairs
    """
    try:
        limit = int(request.args.get('limit', 10))
        routes = db_handler.get_top_routes(limit)
        
        # Apply custom sorting algorithm for ranking
        if routes:
            sorter = CustomSort()
            routes = sorter.sort_by_trip_count(routes)
        
        return jsonify(routes)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analysis/payment', methods=['GET'])
def get_payment_analysis():
    """
    Get payment type distribution (credit card, cash, etc.)
    
    Returns:
        JSON: Breakdown of trips by payment method
    """
    try:
        analysis = db_handler.get_payment_analysis()
        return jsonify(analysis)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analysis/speed', methods=['GET'])
def get_speed_analysis():
    """
    Get average speed analysis by hour of day
    
    Returns:
        JSON: Speed patterns throughout the day (mph or km/h)
    """
    try:
        analysis = db_handler.get_speed_analysis()
        return jsonify(analysis)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analysis/tips', methods=['GET'])
def get_tip_analysis():
    """
    Get tip percentage analysis and patterns
    
    Returns:
        JSON: Tipping statistics including average tips, ranges, and patterns
    """
    try:
        analysis = db_handler.get_tip_analysis()
        return jsonify(analysis)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# API ENDPOINTS - CUSTOM INSIGHTS


@app.route('/api/insights/custom', methods=['GET'])
def get_custom_insights():
    """
    Get insights using custom algorithms (outlier detection, aggregation)
    
    Returns:
        JSON: Custom analysis results including outliers and aggregated data
    """
    try:
        # Fetch trips data for custom analysis
        trips = db_handler.get_trips_for_analysis()
        
        # Apply custom outlier detection algorithm
        outlier_detector = OutlierDetector()
        outliers = outlier_detector.detect_fare_outliers(trips)
        
        # Apply custom aggregation algorithm
        aggregator = TripAggregator()
        aggregated = aggregator.aggregate_by_hour(trips)
        
        return jsonify({
            'outliers_detected': len(outliers),
            'hourly_aggregation': aggregated,
            'outlier_samples': outliers[:10]  # Return sample of outliers
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analysis/weekend-comparison', methods=['GET'])
def get_weekend_comparison():
    """
    Get weekend vs weekday comparison statistics
    
    Returns:
        JSON: Comparative analysis between weekend and weekday patterns
    """
    try:
        comparison = db_handler.get_weekend_comparison()
        return jsonify(comparison)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
  
