
# DATABASE OPERATIONS MODULE

# This module handles all MySQL database operations for the Urban Mobility
# Explorer application. It provides a DatabaseHandler class that manages
# connections, executes queries, and retrieves analysis data.
#
# IMPORTANT: DO NOT RUN THIS FILE DIRECTLY
# This module is imported and used by app.py (Flask API server)


# Standard library imports
import os

# Third-party imports
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

# Load environment variables from .env file
# This file should contain DB_HOST, DB_USER, DB_PASSWORD, DB_NAME, DB_PORT
load_dotenv()


# DATABASE HANDLER CLASS


class DatabaseHandler:
    """
    Handles all database connections and queries for NYC taxi trip data.
    
    This class manages MySQL database connections and provides methods for:
    - Establishing database connections
    - Executing queries with parameters
    - Retrieving summary statistics
    - Filtering and analyzing trip data
    - Generating insights and reports
    """
    
    def __init__(self):
        """
        Initialize DatabaseHandler with MySQL connection parameters.
        
        Reads database credentials from environment variables for security.
        Falls back to default values if environment variables are not set.
        """
        # MySQL connection configuration from environment variables
        self.db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),      # Database server address
            'user': os.getenv('DB_USER', 'root'),           # Database username
            'password': os.getenv('DB_PASSWORD', ''),       # Database password
            'database': os.getenv('DB_NAME', 'urban_mobility'),  # Database name
            'port': int(os.getenv('DB_PORT', 3306))         # Database port (default MySQL port)
        }
    
    
    # CONNECTION MANAGEMENT METHODS
    
    
    def get_connection(self):
        """
        Create and return a new MySQL database connection.
        
        Returns:
            connection object if successful, None if connection fails
            
        Note:
            Connection should be closed after use to prevent resource leaks
        """
        try:
            # Establish connection using stored configuration
            conn = mysql.connector.connect(**self.db_config)
            return conn
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            return None
    
    def execute_query(self, query, params=None):
        """
        Execute a SQL query and return results.
        
        Args:
            query (str): SQL query string (use %s for parameters)
            params (tuple): Optional query parameters for safe parameterization
            
        Returns:
            list: List of dictionaries representing rows, or None on error
            
        Note:
            Uses parameterized queries to prevent SQL injection attacks
        """
        # Establish database connection
        conn = self.get_connection()
        if not conn:
            return None
        
        try:
            # Create cursor that returns rows as dictionaries for easy access
            cursor = conn.cursor(dictionary=True)
            
            # Execute query with parameters (prevents SQL injection)
            cursor.execute(query, params or ())
            
            # Fetch all results from the query
            results = cursor.fetchall()
            
            return results
        except Error as e:
            print(f"Error executing query: {e}")
            return None
        finally:
            # Always close cursor and connection to free resources
            cursor.close()
            conn.close()
    
    
    # DATA RETRIEVAL METHODS - STATISTICS & ANALYSIS
    
    def get_summary_stats(self):
        """
        Get overall summary statistics for the entire dataset.
        
        Returns:
            dict: Summary statistics including:
                - total_trips: Total number of trips in database
                - avg_distance: Average trip distance in miles
                - avg_fare: Average fare amount
                - avg_total: Average total amount paid
                - avg_passengers: Average passenger count
                - total_revenue: Sum of all fares
                - avg_duration: Average trip duration in minutes
                - avg_speed: Average trip speed in mph
                - avg_tip_pct: Average tip percentage
                - earliest_trip: First trip datetime
                - latest_trip: Last trip datetime
        """
        query = """
        SELECT 
            COUNT(*) as total_trips,              -- Total number of trips
            AVG(trip_distance) as avg_distance,   -- Average miles per trip
            AVG(fare_amount) as avg_fare,         -- Average fare charged
            AVG(total_amount) as avg_total,       -- Average total cost
            AVG(passenger_count) as avg_passengers, -- Average passengers per trip
            SUM(fare_amount) as total_revenue,    -- Total revenue generated
            AVG(duration_mins) as avg_duration,   -- Average trip length in minutes
            AVG(avg_speed_mph) as avg_speed,      -- Average speed in mph
            AVG(tip_percentage) as avg_tip_pct,   -- Average tip percentage
            MIN(tpep_pickup_datetime) as earliest_trip,  -- First trip in dataset
            MAX(tpep_pickup_datetime) as latest_trip     -- Last trip in dataset
        FROM trips
        """
        result = self.execute_query(query)
        return result[0] if result else {}
    
    def get_trips(self, limit=100, offset=0, borough=None, min_fare=None, max_fare=None,
                  min_distance=None, max_distance=None, start_date=None, end_date=None,
                  hour=None, is_weekend=None):
        """
        Get trips with optional filtering and pagination.
        
        Args:
            limit (int): Maximum number of records to return
            offset (int): Number of records to skip (for pagination)
            borough (str): Filter by pickup borough
            min_fare (float): Minimum fare amount
            max_fare (float): Maximum fare amount
            min_distance (float): Minimum trip distance in miles
            max_distance (float): Maximum trip distance in miles
            start_date (str): Start date filter (YYYY-MM-DD)
            end_date (str): End date filter (YYYY-MM-DD)
            hour (int): Filter by hour of day (0-23)
            is_weekend (str): 'true' for weekends only, 'false' for weekdays only
            
        Returns:
            list: List of trip records matching the filters
        """
        # Base query selecting all relevant trip fields
        query = """
        SELECT 
            id,
            tpep_pickup_datetime,
            tpep_dropoff_datetime,
            passenger_count,
            trip_distance,
            fare_amount,
            tip_amount,
            total_amount,
            payment_type,
            pu_borough,           -- Pickup borough
            pu_zone,              -- Pickup zone name
            do_borough,           -- Dropoff borough
            do_zone,              -- Dropoff zone name
            duration_mins,        -- Trip duration
            avg_speed_mph,        -- Average speed
            tip_percentage,       -- Calculated tip percentage
            fare_range,           -- Fare bracket category
            distance_category     -- Distance category
        FROM trips
        WHERE 1=1                 -- Base condition for adding filters
        """
        params = []  # List to hold query parameters

        # Apply filters dynamically based on provided parameters
        
        if borough:
            query += " AND pu_borough = %s"
            params.append(borough)

        if min_fare:
            query += " AND fare_amount >= %s"
            params.append(float(min_fare))

        if max_fare:
            query += " AND fare_amount <= %s"
            params.append(float(max_fare))

        if min_distance:
            query += " AND trip_distance >= %s"
            params.append(float(min_distance))

        if max_distance:
            query += " AND trip_distance <= %s"
            params.append(float(max_distance))

        if start_date:
            query += " AND DATE(tpep_pickup_datetime) >= DATE(%s)"
            params.append(start_date)

        if end_date:
            query += " AND DATE(tpep_pickup_datetime) <= DATE(%s)"
            params.append(end_date)

        if hour is not None and hour != '':
            query += " AND pickup_hour = %s"
            params.append(int(hour))

        # Weekend filter: 1=Sunday, 7=Saturday in MySQL DAYOFWEEK()
        if is_weekend == 'true':
            query += " AND DAYOFWEEK(tpep_pickup_datetime) IN (1,7)"
        elif is_weekend == 'false':
            query += " AND DAYOFWEEK(tpep_pickup_datetime) NOT IN (1,7)"

        # Order by most recent trips first, apply pagination
        query += " ORDER BY tpep_pickup_datetime DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])

        return self.execute_query(query, tuple(params))
    
    def get_hourly_patterns(self):
        """
        Get trip patterns aggregated by hour of day (0-23).
        
        Returns:
            list: Hourly statistics showing how trip characteristics vary by time
        """
        query = """
        SELECT 
            pickup_hour,                       -- Hour of day (0-23)
            COUNT(*) as trip_count,            -- Number of trips in this hour
            AVG(fare_amount) as avg_fare,      -- Average fare for this hour
            AVG(trip_distance) as avg_distance,-- Average distance traveled
            AVG(duration_mins) as avg_duration,-- Average trip duration
            AVG(avg_speed_mph) as avg_speed,   -- Average speed (indicates traffic)
            AVG(tip_percentage) as avg_tip_pct -- Average tip percentage
        FROM trips
        GROUP BY pickup_hour
        ORDER BY pickup_hour
        """
        return self.execute_query(query)
    
    def get_borough_analysis(self):
        """
        Get analysis grouped by NYC borough.
        
        Returns:
            list: Statistics for each borough (Manhattan, Brooklyn, Queens, Bronx, Staten Island)
            
        Note:
            Filters out NULL and 'Unknown' boroughs for cleaner results
        """
        query = """
        SELECT 
            pu_borough as Borough,             -- Borough name
            COUNT(*) as total_trips,           -- Total trips from this borough
            AVG(fare_amount) as avg_fare,      -- Average fare from this borough
            AVG(trip_distance) as avg_distance,-- Average trip distance
            AVG(duration_mins) as avg_duration,-- Average trip duration
            AVG(tip_percentage) as avg_tip_pct,-- Average tip percentage
            SUM(fare_amount) as total_revenue  -- Total revenue from this borough
        FROM trips
        WHERE pu_borough IS NOT NULL AND pu_borough != 'Unknown'  -- Exclude invalid data
        GROUP BY pu_borough
        ORDER BY total_trips DESC              -- Most popular boroughs first
        """
        return self.execute_query(query)
    
    def get_fare_distribution(self):
        """
        Get fare amount distribution across different price ranges.
        
        Returns:
            list: Count of trips in each fare bracket ($0-10, $10-20, etc.)
        """
        query = """
        SELECT 
            fare_range,                        -- Fare bracket category
            COUNT(*) as trip_count             -- Number of trips in this bracket
        FROM trips
        GROUP BY fare_range
        ORDER BY 
            CASE fare_range                    -- Custom sort order for fare ranges
                WHEN '$0-10' THEN 1
                WHEN '$10-20' THEN 2
                WHEN '$20-30' THEN 3
                WHEN '$30-50' THEN 4
                WHEN '$50+' THEN 5
            END
        """
        return self.execute_query(query)
    