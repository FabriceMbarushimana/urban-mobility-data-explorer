
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
    
    # ========================================================================
    # CONNECTION MANAGEMENT METHODS
    # ========================================================================
    
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
    
    # ========================================================================
    # DATA RETRIEVAL METHODS - STATISTICS & ANALYSIS
    # ========================================================================