import pandas as pd
import mysql.connector
from mysql.connector import errorcode

class MySQLInserter:
    def __init__(self, host="localhost", user="root", database="urban_mobility"):
        try:
            self.conn = mysql.connector.connect(
                host=host,
                user=user,
                database=database
            )
            self.cursor = self.conn.cursor()
            print("[INFO] Connected to MySQL database successfully")
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("[ERROR] Access denied: Check username or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print(f"[ERROR] Database {database} does not exist")
            else:
                print(err)
            raise

    def insert_zones(self, zones_df):
        query = """
        INSERT INTO zones (zone_id, borough, zone_name, service_zone, geometry)
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            borough=VALUES(borough),
            zone_name=VALUES(zone_name),
            service_zone=VALUES(service_zone),
            geometry=VALUES(geometry)
        """
        data = [
            (
                row.zone_id,
                row.borough,
                row.zone_name,
                row.service_zone,
                row.geometry if 'geometry' in row._fields else None
            )
            for row in zones_df.itertuples()
        ]
        self.cursor.executemany(query, data)
        self.conn.commit()
        print(f"[INFO] Inserted/Updated {len(data)} zones")

    def insert_trips(self, trips_df):
        query = """
        INSERT INTO trips (
            pickup_datetime,
            dropoff_datetime,
            pickup_zone_id,
            dropoff_zone_id,
            trip_distance,
            fare_amount,
            total_amount,
            trip_duration_minutes,
            fare_per_mile,
            pickup_hour
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """
        data = [
            (
                row.pickup_datetime,
                row.dropoff_datetime,
                row.pickup_zone_id,
                row.dropoff_zone_id,
                row.trip_distance,
                row.fare_amount,
                row.total_amount,
                row.trip_duration_minutes,
                row.fare_per_mile,
                row.pickup_hour
            )
            for row in trips_df.itertuples()
        ]
        self.cursor.executemany(query, data)
        self.conn.commit()
        print(f"[INFO] Inserted {len(data)} trips")

    def close(self):
        self.cursor.close()
        self.conn.close()
        print("[INFO] MySQL connection closed")


if __name__ == "__main__":
    zones_df = pd.read_csv("../data/cleaned/zones_cleaned.csv")
    trips_df = pd.read_csv("../data/cleaned/trips_cleaned.csv")
    inserter = MySQLInserter()
    inserter.insert_zones(zones_df)
    inserter.insert_trips(trips_df)
    inserter.close()
    print("=== Data insertion completed successfully ===")
