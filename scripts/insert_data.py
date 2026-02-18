import pandas as pd
import mysql.connector
from mysql.connector import errorcode
import os
from dotenv import load_dotenv
import numpy as np

load_dotenv()

class MySQLInserter:
    def __init__(self):
        self.host = os.getenv("DB_HOST", "localhost")
        self.user = os.getenv("DB_USER", "root")
        self.password = os.getenv("DB_PASSWORD", "")
        self.database = os.getenv("DB_NAME", "urban_mobility")
        self.port = int(os.getenv("DB_PORT", 3306))
        self.ssl_ca = os.getenv("DB_SSL_CA")

        print(f"[INFO] Connecting to database {self.database} at {self.host}...")
        try:
            config = {
                "host": self.host,
                "user": self.user,
                "password": self.password,
                "database": self.database,
                "port": self.port
            }
            if self.ssl_ca:
                config["ssl_ca"] = self.ssl_ca
                config["ssl_verify_cert"] = True

            self.conn = mysql.connector.connect(**config)
            self.cursor = self.conn.cursor()
            print("[INFO] Connected to MySQL database successfully")
        except mysql.connector.Error as err:
            print(f"[ERROR] Connection failed: {err}")
            raise

    def insert_zones(self, zones_df):
        print("[INFO] preparing zones insertion...")
        query = """
        INSERT INTO zones (zone_id, borough, zone_name, service_zone)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            borough=VALUES(borough),
            zone_name=VALUES(zone_name),
            service_zone=VALUES(service_zone)
        """

        zones_df = zones_df.fillna("Unknown")

        data = []
        for row in zones_df.itertuples():
            data.append((
                row.LocationID,
                row.Borough,
                row.Zone,
                row.service_zone
            ))

        try:
            self.cursor.executemany(query, data)
            self.conn.commit()
            print(f"[INFO] Inserted/Updated {len(data)} zones")
        except mysql.connector.Error as err:
            print(f"[ERROR] Failed inserting zones: {err}")

    def get_valid_zone_ids(self):
        query = "SELECT zone_id FROM zones"
        self.cursor.execute(query)
        return {row[0] for row in self.cursor.fetchall()}

    def insert_trips_chunk(self, trips_chunk, valid_zone_ids):
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

        trips_chunk = trips_chunk.replace({np.nan: None})

        data = []
        for row in trips_chunk.itertuples():
            if row.PULocationID not in valid_zone_ids or row.DOLocationID not in valid_zone_ids:
                continue

            data.append((
                row.tpep_pickup_datetime,
                row.tpep_dropoff_datetime,
                row.PULocationID,
                row.DOLocationID,
                row.trip_distance,
                row.fare_amount,
                row.total_amount,
                row.trip_duration_minutes,
                row.fare_per_mile,
                row.pickup_hour
            ))

        if not data:
            return 0

        try:
            self.cursor.executemany(query, data)
            self.conn.commit()
            return len(data)
        except mysql.connector.Error as err:
            print(f"\n[ERROR] Failed inserting batch: {err}")
            self.conn.rollback()
            return 0

    def close(self):
        if hasattr(self, 'cursor') and self.cursor:
            self.cursor.close()
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()
        print("\n[INFO] MySQL connection closed")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)

    zones_path = os.path.join(project_root, "data", "processed", "zone_lookup.csv")
    trips_path = os.path.join(project_root, "data", "processed", "processed_trip_data_20260218_195244.csv")

    inserter = None
    try:
        inserter = MySQLInserter()

        if os.path.exists(zones_path):
            print(f"[INFO] Loading zones from: {zones_path}")
            zones_df = pd.read_csv(zones_path)
            inserter.insert_zones(zones_df)
        else:
            print(f"[WARNING] Zones file not found at {zones_path}")

        if os.path.exists(trips_path):
            print(f"[INFO] Loading trips from: {trips_path}")

            print("[INFO] Fetching valid zone IDs from database...")
            valid_zone_ids = inserter.get_valid_zone_ids()
            print(f"[INFO] Found {len(valid_zone_ids)} valid zones.")

            chunk_size = 10000
            print(f"[INFO] Processing trips in chunks of {chunk_size}...")

            total_inserted = 0
            with pd.read_csv(trips_path, chunksize=chunk_size) as reader:
                for i, chunk in enumerate(reader):
                    count = inserter.insert_trips_chunk(chunk, valid_zone_ids)
                    total_inserted += count
                    print(f"\r[INFO] Processed chunk {i+1} | Total trips inserted: {total_inserted}", end="", flush=True)

            print(f"\n[INFO] Finished inserting trips. Grand total: {total_inserted}")
        else:
            print(f"[ERROR] Trips file not found at {trips_path}")

    except Exception as e:
        print(f"\n[ERROR] An unexpected error occurred: {e}")
    finally:
        if inserter:
            inserter.close()
        print("=== Script execution finished ===")

