
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
