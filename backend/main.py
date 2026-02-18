from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from mysql.connector import errorcode
from dotenv import load_dotenv
import os
import time
import decimal


load_dotenv()

app = Flask(__name__)
CORS(app)


def default_serializer(obj):
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    raise TypeError

def get_db_connection():
    """Establishes a connection to the Cloud MySQL database."""
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
            database=os.getenv("DB_NAME", "urban_mobility"),
            port=int(os.getenv("DB_PORT", 3306)),
            ssl_ca=os.getenv("DB_SSL_CA"),
            ssl_verify_cert=True if os.getenv("DB_SSL_CA") else False
        )
        return conn
    except mysql.connector.Error as err:
        print(f"[ERROR] Database connection failed: {err}")
        return None

def serialize_rows(rows):
    """Helper to convert Decimal objects to floats in a list of dicts."""
    for row in rows:
        for key, value in row.items():
            if isinstance(value, decimal.Decimal):
                row[key] = float(value)
    return rows

@app.route('/api/trips', methods=['GET'])
def get_trips():
    """
    Fetch trips with optional filtering by borough.
    Uses SQL JOIN for efficient filtering.
    """

    borough = request.args.get('borough')
    limit = int(request.args.get('limit', 100))
    offset = int(request.args.get('offset', 0))

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = conn.cursor(dictionary=True)

    try:

        query = """
            SELECT t.*, z.borough as pickup_borough, z.zone_name as pickup_zone
            FROM trips t
            JOIN zones z ON t.pickup_zone_id = z.zone_id
        """
        params = []


        if borough:
            query += " WHERE z.borough = %s"
            params.append(borough)


        query += " LIMIT %s OFFSET %s"
        params.append(limit)
        params.append(offset)

        cursor.execute(query, params)
        trips = cursor.fetchall()


        return jsonify(serialize_rows(trips))

    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500
    finally:
        cursor.close()
        conn.close()



def manual_bubble_sort(data_list, key, descending=False):
    """
    Manual implementation of Bubble Sort.

    Time Complexity: O(n^2) - Nested loops iterate through the list.
                              For each element, we compare it with n-1 other elements.
    Space Complexity: O(1) - Sorting is done in-place, requiring no extra memory proportional to input size.

    Args:
        data_list (list): List of dictionaries to sort.
        key (str): The dictionary key to sort by (e.g., 'fare_amount').
        descending (bool): If True, sort from high to low.
    """
    n = len(data_list)
    for i in range(n):

        for j in range(0, n - i - 1):
            val_a = data_list[j].get(key, 0) or 0
            val_b = data_list[j + 1].get(key, 0) or 0

            should_swap = False
            if descending:
                if val_a < val_b:
                    should_swap = True
            else:
                if val_a > val_b:
                    should_swap = True

            if should_swap:

                data_list[j], data_list[j + 1] = data_list[j + 1], data_list[j]
    return data_list

@app.route('/api/top_fares', methods=['GET'])
def get_top_fares():
    """
    Demonstrates usage of MANUAL ALGORITHMS (Bubble Sort).
    Fetches raw data and sorts it in Python rather than SQL.
    """
    borough = request.args.get('borough', 'Manhattan')
    limit = int(request.args.get('limit', 50))

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = conn.cursor(dictionary=True)

    try:


        query = """
            SELECT t.pickup_datetime, t.dropoff_datetime, t.fare_amount, t.trip_distance,
                   z.borough as pickup_borough
            FROM trips t
            JOIN zones z ON t.pickup_zone_id = z.zone_id
            WHERE z.borough = %s
            LIMIT 500
        """
        cursor.execute(query, (borough,))
        raw_trips = cursor.fetchall()


        trip_data = serialize_rows(raw_trips)


        start_time = time.time()
        sorted_trips = manual_bubble_sort(trip_data, key='fare_amount', descending=True)
        end_time = time.time()
        time_taken = end_time - start_time

        response = {
            "meta": {
                "count": len(sorted_trips),
                "algorithm": "Bubble Sort (Manual)",
                "time_taken_seconds": time_taken,
                "complexity": "O(n^2)",
                "note": "Sorted manually in Python, not via SQL ORDER BY"
            },
            "data": sorted_trips[:limit]
        }
        return jsonify(response)

    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """
    Returns aggregated statistics about the dataset.
    """
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT
                COUNT(*) as total_trips,
                AVG(fare_amount) as avg_fare,
                AVG(trip_distance) as avg_distance,
                SUM(total_amount) as total_revenue
            FROM trips
        """)
        stats = cursor.fetchone()
        return jsonify(serialize_rows([stats])[0])
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    app.run(debug=True, port=5001)

