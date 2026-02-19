# URBAN MOBILITY DATA PIPELINE - ETL Script
# This script performs Extract, Transform, Load (ETL) operations for NYC taxi data:
# 1. Loads CSV data files and shapefiles
# 2. Cleans and validates data (removes outliers, invalid dates)
# 3. Engineers features (speed, duration, categories)
# 4. Loads data into MySQL database
# 5. Exports GeoJSON for mapping
#
# USAGE: python main.py (run once to initialize database)

# Standard library imports
import os
import json

# Third-party imports for data processing
import pandas as pd              # Data manipulation and analysis
import geopandas as gpd          # Geospatial data handling
import mysql.connector           # MySQL database connector
from mysql.connector import Error
from dotenv import load_dotenv   # Environment variable management

# ENVIRONMENT CONFIGURATION
# Load database credentials and configuration from .env file
load_dotenv()

# PATH CONFIGURATION
# Configure all file paths relative to script location for portability
BASE_PATH = os.path.dirname(os.path.abspath(__file__))  # backend/ directory
REPO_ROOT = os.path.dirname(BASE_PATH)                   # project root directory
DATA_DIR = os.path.join(REPO_ROOT, 'data')               # raw data location

# Output directories for processed and rejected data
OUTPUT_DIR = os.path.join(BASE_PATH, 'processed')        # cleaned data output
REJECTED_DIR = os.path.join(BASE_PATH, 'rejected_data')  # invalid records storage
os.makedirs(OUTPUT_DIR, exist_ok=True)                   # create if doesn't exist
os.makedirs(REJECTED_DIR, exist_ok=True)

# Input data file paths
TRIP_DATA = os.path.join(DATA_DIR, 'yellow_tripdata_2019-01.csv')  # NYC taxi trip records
ZONE_LOOKUP = os.path.join(DATA_DIR, 'taxi_zone_lookup.csv')       # Zone/Borough mapping
TAXI_ZONES_JSON = os.path.join(DATA_DIR, 'taxi_zones.json')        # Taxi zones geographic data
SPATIAL_DATA = os.path.join(DATA_DIR, 'taxi_zones.shp')            # Geographic boundaries

# Output file paths
GEOJSON_OUT = os.path.join(OUTPUT_DIR, 'taxi_zones_final.json')   # Map visualization file
REJECTED_RECORDS = os.path.join(REJECTED_DIR, 'invalid_dates.csv')# Rejected trip records
REJECTION_LOG = os.path.join(REJECTED_DIR, 'rejection_report.txt')# Rejection summary

# DATABASE CONFIGURATION
# MySQL connection parameters loaded from environment variables
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),           # Database server address
    'user': os.getenv('DB_USER', 'root'),                # Database username
    'password': os.getenv('DB_PASSWORD', ''),            # Database password (from .env)
    'database': os.getenv('DB_NAME', 'urban_mobility'),  # Target database name
    'port': int(os.getenv('DB_PORT', 3306))              # MySQL port (default: 3306)
}

# DATA VALIDATION RULES
# Cutoff year: Accept any year up to 2019, reject 2020 and onwards
# This ensures we only work with historical 2019 data
CUTOFF_YEAR = 2019

# PIPELINE START
print("\n" + "="*70)
print("URBAN MOBILITY DATA PIPELINE - ETL PROCESS")
print("="*70)
print("Initializing data extraction, transformation, and loading...\n")

# STEP 1: DATA EXTRACTION (LOADING)
# Validate that required data files exist before proceeding
if not os.path.exists(TRIP_DATA):
    print(f"ERROR: Could not find trip data file at {TRIP_DATA}")
    print("   Please ensure the data file exists in the data/ directory.")
    exit()

print("STEP 1: Loading data files...")
print("-" * 70)

# Load trip records (limited to 15,000 rows for faster processing)
# After cleaning, approximately 10,000-12,000 valid records remain
print("   > Loading taxi trip data (15,000 rows sample)...")
trips = pd.read_csv(TRIP_DATA, low_memory=False, nrows=15000)
print(f"   [OK] Loaded {len(trips):,} trip records")

# Load zone lookup table (maps LocationID to Borough and Zone names)
print("   > Loading zone lookup table...")
lookup = pd.read_csv(ZONE_LOOKUP)
print(f"   [OK] Loaded {len(lookup)} zones")

# Load taxi zones geographic data (objectid, shape_leng, shape_area, zone, locationid, borough)
print("   > Loading taxi zones geographic data...")
with open(TAXI_ZONES_JSON, 'r') as f:
    taxi_zones_data = json.load(f)
print(f"   [OK] Loaded {len(taxi_zones_data)} taxi zones")

# Load spatial data (shapefile with geographic boundaries for mapping)
print("   > Loading spatial data (shapefiles)...")
zones_spatial = gpd.read_file(SPATIAL_DATA)
print(f"   [OK] Loaded {len(zones_spatial)} geographic zones")

# STEP 2: DATA INTEGRATION (MERGING)
print("\nSTEP 2: Integrating datasets...")
print("-" * 70)

# Merge trip data with pickup zone information
print("   > Joining trip data with pickup zone information...")
df = trips.merge(lookup, left_on='PULocationID', right_on='LocationID', how='left')
df = df.rename(columns={'Borough': 'pu_borough', 'Zone': 'pu_zone'})
print("   [OK] Pickup zones merged successfully")

# Add dropoff zone/borough information
print("   > Joining trip data with dropoff zone information...")
lookup_do = lookup.rename(
    columns={
        'LocationID': 'DOLocationID',      # Rename to match dropoff location ID
        'Borough': 'do_borough',            # Dropoff borough
        'Zone': 'do_zone',                  # Dropoff zone name
        'service_zone': 'do_service_zone'   # Dropoff service zone
    }
)
df = df.merge(lookup_do, on='DOLocationID', how='left')
print("   [OK] Dropoff zones merged successfully")
print(f"   [OK] Final merged dataset: {len(df):,} records with {len(df.columns)} columns")


# STEP 3: DATA CLEANING & VALIDATION
print("\nSTEP 3: Cleaning and validating data...")
print("-" * 70)
initial_count = len(df)
print(f"   Starting with {initial_count:,} records")

# Convert datetime columns to proper datetime objects
print("   > Parsing datetime columns...")
df['tpep_pickup_datetime'] = pd.to_datetime(df['tpep_pickup_datetime'], errors='coerce')
df['tpep_dropoff_datetime'] = pd.to_datetime(df['tpep_dropoff_datetime'], errors='coerce')
print("   [OK] Datetime columns parsed")

# Convert numeric columns to proper data types (faster filtering and calculations)
print("   > Converting numeric columns to appropriate types...")
df['trip_distance'] = pd.to_numeric(df['trip_distance'], errors='coerce')
df['fare_amount'] = pd.to_numeric(df['fare_amount'], errors='coerce')
df['passenger_count'] = pd.to_numeric(df['passenger_count'], errors='coerce')
print("   [OK] Numeric columns validated")

# Validate dates: Accept any year up to 2019, reject 2020 onwards
print(f"   > Validating date ranges (accepting year <= {CUTOFF_YEAR})...")

# Use vectorized operations for performance (faster than row-by-row iteration)
pickup_year = df['tpep_pickup_datetime'].dt.year
dropoff_year = df['tpep_dropoff_datetime'].dt.year
invalid_mask = (pickup_year > CUTOFF_YEAR) | (dropoff_year > CUTOFF_YEAR)
invalid_dates = df[invalid_mask]

if len(invalid_dates) > 0:
    print(f"   [WARNING] Found {len(invalid_dates):,} records with invalid dates (year {CUTOFF_YEAR + 1}+)")
    
    # Save rejected records for audit trail
    invalid_dates.to_csv(REJECTED_RECORDS, index=False)
    
    # Generate detailed rejection report
    with open(REJECTION_LOG, 'w') as f:
        f.write(f"Date Validation Report\n")
        f.write(f"======================\n\n")
        f.write(f"Valid Year Range: <= {CUTOFF_YEAR}\n")
        f.write(f"Rejected Year Range: {CUTOFF_YEAR + 1}+\n")
        f.write(f"Total Invalid Records: {len(invalid_dates):,}\n\n")
        f.write(f"Sample Invalid Records (first 10):\n")
        f.write(invalid_dates.head(10).to_string())
    
    print(f"   [OK] Rejected records exported to: {REJECTED_RECORDS}")
    print(f"   [OK] Detailed rejection report saved to: {REJECTION_LOG}")
else:
    print(f"   [OK] All dates are valid (within acceptable range)")

# Remove invalid date records from dataset
df = df[~invalid_mask]

print("   > Filtering outliers and invalid values...")
# Filter outliers using vectorized operations (much faster than iterating)
# Remove records with: zero distance, zero fare, zero passengers, or missing dates
valid_mask = (
    (df['trip_distance'] > 0) &           # Valid trip distance
    (df['fare_amount'] > 0) &             # Positive fare amount
    (df['passenger_count'] > 0) &         # At least one passenger
    (df['tpep_pickup_datetime'].notna()) & # Valid pickup datetime
    (df['tpep_dropoff_datetime'].notna())  # Valid dropoff datetime
)
df = df[valid_mask]

records_removed = initial_count - len(df)
print(f"   [OK] Removed {records_removed:,} invalid/outlier records")
print(f"   [OK] Clean dataset: {len(df):,} valid records ({(len(df)/initial_count)*100:.1f}% retention)")



# STEP 4: FEATURE ENGINEERING
print("\nSTEP 4: Engineering new features...")
print("-" * 70)

# Calculate trip duration in minutes
print("   > Calculating trip duration...")
df['duration_mins'] = (df['tpep_dropoff_datetime'] - df['tpep_pickup_datetime']).dt.total_seconds() / 60
print(f"   [OK] Duration calculated (avg: {df['duration_mins'].mean():.1f} minutes)")

# Remove records with invalid duration (negative or zero)
df = df[df['duration_mins'] > 0]

# Calculate average speed in miles per hour
print("   > Calculating average speed...")
df['avg_speed_mph'] = df['trip_distance'] / (df['duration_mins'] / 60)
print(f"   [OK] Speed calculated (avg: {df['avg_speed_mph'].mean():.1f} mph)")

# Calculate tip percentage
print("   > Calculating tip percentages...")
df['tip_percentage'] = (df['tip_amount'] / df['fare_amount']) * 100
print(f"   [OK] Tip percentage calculated (avg: {df['tip_percentage'].mean():.1f}%)")

# Extract hour of day from pickup datetime (for hourly patterns analysis)
print("   > Extracting temporal features...")
df['pickup_hour'] = df['tpep_pickup_datetime'].dt.hour
print("   [OK] Pickup hour extracted")

# Create fare range categories for distribution analysis
print("   > Creating fare range categories...")
df['fare_range'] = pd.cut(
    df['fare_amount'],
    bins=[0, 5, 10, 20, 50, float('inf')],       # Fare brackets
    labels=['0-5', '5-10', '10-20', '20-50', '50+'],  # Category labels
    right=False                                   # Left-inclusive intervals
)
print("   [OK] Fare ranges categorized (5 brackets)")

# Create distance categories for trip length analysis
print("   > Creating distance categories...")
df['distance_category'] = pd.cut(
    df['trip_distance'],
    bins=[0, 1, 3, 5, 10, float('inf')],         # Distance brackets in miles
    labels=['0-1', '1-3', '3-5', '5-10', '10+'], # Category labels
    right=False                                   # Left-inclusive intervals
)
print("   [OK] Distance categories created (5 brackets)")
print(f"\n   [INFO] Feature engineering complete: {len(df.columns)} total columns")


# STEP 5: DATABASE STORAGE (LOADING)
print("\nSTEP 5: Loading data into MySQL database...")
print("-" * 70)

# Initialize variables for scope (used in final summary)
zone_values = []
taxi_zones_values = []
total_rows = 0

try:
    # Establish connection to MySQL server (without specifying database)
    print("   > Connecting to MySQL server...")
    conn = mysql.connector.connect(
        host=DB_CONFIG['host'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        port=DB_CONFIG['port']
    )
    cursor = conn.cursor()
    print(f"   [OK] Connected to MySQL server at {DB_CONFIG['host']}:{DB_CONFIG['port']}")
    
    # Optimize MySQL packet size for large batch inserts
    print("   > Optimizing MySQL configuration...")
    try:
        cursor.execute("SET GLOBAL max_allowed_packet=67108864")  # 64MB packet size
        print("   [OK] MySQL packet size limit increased to 64MB")
    except mysql.connector.Error:
        print("   [INFO] Using default MySQL packet size (batch operations adjusted)")
    
    # Create database if it doesn't exist and switch to it
    print(f"   > Setting up database '{DB_CONFIG['database']}'...")
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
    cursor.execute(f"USE {DB_CONFIG['database']}")
    print(f"   [OK] Database '{DB_CONFIG['database']}' ready")
    
    # Drop existing tables to ensure clean slate (prevents duplicate data)
    print("   > Dropping existing tables (if any)...")
    cursor.execute("DROP TABLE IF EXISTS trips")
    cursor.execute("DROP TABLE IF EXISTS taxi_zones")
    cursor.execute("DROP TABLE IF EXISTS zones")
    cursor.execute("DROP TABLE IF EXISTS excluded_data_log")
    print("   [OK] Old tables removed (fresh start)")
    
    # Create zones table (referenced by taxi_zones and trips)
    create_zones_table = """
    CREATE TABLE zones (
        LocationID INT PRIMARY KEY,
        Borough VARCHAR(50),
        Zone VARCHAR(100),
        service_zone VARCHAR(50),
        INDEX idx_borough (Borough),
        INDEX idx_zone (Zone)
    )
    """
    cursor.execute(create_zones_table)
    
    # Create taxi_zones table with foreign key to zones
    create_taxi_zones_table = """
    CREATE TABLE taxi_zones (
        objectid INT PRIMARY KEY,
        shape_leng FLOAT,
        shape_area FLOAT,
        zone VARCHAR(100),
        locationid INT,
        borough VARCHAR(50),
        INDEX idx_locationid (locationid),
        INDEX idx_borough_tz (borough),
        FOREIGN KEY (locationid) REFERENCES zones(LocationID) ON DELETE CASCADE
    )
    """
    cursor.execute(create_taxi_zones_table)
    
    # Create trips table with proper schema and foreign keys
    create_trips_table = """
    CREATE TABLE trips (
        id INT AUTO_INCREMENT PRIMARY KEY,
        VendorID INT,
        tpep_pickup_datetime DATETIME,
        tpep_dropoff_datetime DATETIME,
        passenger_count INT,
        trip_distance FLOAT,
        RatecodeID INT,
        store_and_fwd_flag VARCHAR(10),
        PULocationID INT,
        DOLocationID INT,
        payment_type INT,
        fare_amount FLOAT,
        extra FLOAT,
        mta_tax FLOAT,
        tip_amount FLOAT,
        tolls_amount FLOAT,
        improvement_surcharge FLOAT,
        total_amount FLOAT,
        congestion_surcharge FLOAT,
        pu_borough VARCHAR(50),
        pu_zone VARCHAR(100),
        service_zone VARCHAR(50),
        do_borough VARCHAR(50),
        do_zone VARCHAR(100),
        do_service_zone VARCHAR(50),
        duration_mins FLOAT,
        avg_speed_mph FLOAT,
        tip_percentage FLOAT,
        pickup_hour INT,
        fare_range VARCHAR(20),
        distance_category VARCHAR(20),
        INDEX idx_pickup_datetime (tpep_pickup_datetime),
        INDEX idx_pickup_location (PULocationID),
        INDEX idx_dropoff_location (DOLocationID),
        INDEX idx_pickup_hour (pickup_hour),
        INDEX idx_fare_range (fare_range),
        INDEX idx_distance_category (distance_category),
        FOREIGN KEY (PULocationID) REFERENCES zones(LocationID) ON DELETE SET NULL,
        FOREIGN KEY (DOLocationID) REFERENCES zones(LocationID) ON DELETE SET NULL
    )
    """
    cursor.execute(create_trips_table)
    
    # Create excluded_data_log table for tracking data quality issues
    create_excluded_log_table = """
    CREATE TABLE excluded_data_log (
        log_id INT AUTO_INCREMENT PRIMARY KEY,
        issue_type VARCHAR(50),
        trip_identifier VARCHAR(100),
        field_name VARCHAR(50),
        issue_description TEXT,
        action_taken VARCHAR(100),
        logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_issue_type (issue_type),
        INDEX idx_logged_at (logged_at)
    )
    """
    cursor.execute(create_excluded_log_table)
    
    print("   [OK] Database schema created successfully")
    print("        - zones table (4 columns, 2 indexes)")
    print("        - taxi_zones table (6 columns, 2 indexes, 1 FK)")
    print("        - trips table (30 columns, 6 indexes, 2 FKs)")
    print("        - excluded_data_log table (7 columns, 2 indexes)")
    
    # Insert zone lookup data FIRST (required by foreign key constraints)
    print("\n   > Inserting zone lookup data...")
    zone_insert = """
    INSERT INTO zones (LocationID, Borough, Zone, service_zone)
    VALUES (%s, %s, %s, %s)
    """
    zone_values = []
    for _, row in lookup.iterrows():
        zone_values.append((
            int(row['LocationID']),       # Unique zone identifier
            str(row['Borough']),          # Borough name (Manhattan, Brooklyn, etc.)
            str(row['Zone']),             # Specific zone name
            str(row['service_zone'])      # Service zone type
        ))
    cursor.executemany(zone_insert, zone_values)
    conn.commit()
    print(f"   [OK] Zone lookup data inserted ({len(zone_values)} zones)")
    
    # Insert taxi zones geographic data SECOND (depends on zones table)
    print("\n   > Inserting taxi zones geographic data...")
    taxi_zones_insert = """
    INSERT INTO taxi_zones (objectid, shape_leng, shape_area, zone, locationid, borough)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    taxi_zones_values = []
    for zone_data in taxi_zones_data:
        taxi_zones_values.append((
            int(zone_data['objectid']),              # Object ID from GIS data
            float(zone_data['shape_leng']),          # Shape length (perimeter)
            float(zone_data['shape_area']),          # Shape area
            str(zone_data['zone']),                  # Zone name
            int(zone_data['locationid']),            # Location ID (FK to zones)
            str(zone_data['borough'])                # Borough name
        ))
    cursor.executemany(taxi_zones_insert, taxi_zones_values)
    conn.commit()
    print(f"   [OK] Taxi zones geographic data inserted ({len(taxi_zones_values)} zones)")
    
    # Insert trip records LAST (approximately 10,000-12,000 rows after cleaning)
    print("\n   > Inserting trip records into database...")
    batch_size = 1000  # Process 1000 records at a time to avoid memory issues
    total_rows = len(df)
    print(f"     Total records to insert: {total_rows:,}")
    
    for start_idx in range(0, total_rows, batch_size):
        end_idx = min(start_idx + batch_size, total_rows)
        batch = df.iloc[start_idx:end_idx]
        
        # Prepare data for insertion
        insert_query = """
        INSERT INTO trips (
            VendorID, tpep_pickup_datetime, tpep_dropoff_datetime, passenger_count,
            trip_distance, RatecodeID, store_and_fwd_flag, PULocationID, DOLocationID,
            payment_type, fare_amount, extra, mta_tax, tip_amount, tolls_amount,
            improvement_surcharge, total_amount, congestion_surcharge, pu_borough,
            pu_zone, service_zone, do_borough, do_zone, do_service_zone,
            duration_mins, avg_speed_mph, tip_percentage, pickup_hour,
            fare_range, distance_category
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        """
        
        values = []
        for _, row in batch.iterrows():
            # Convert pandas timestamps to Python datetime objects
            pickup_dt = row.get('tpep_pickup_datetime')
            dropoff_dt = row.get('tpep_dropoff_datetime')
            
            if pd.notna(pickup_dt) and hasattr(pickup_dt, 'to_pydatetime'):
                pickup_dt = pickup_dt.to_pydatetime()
            if pd.notna(dropoff_dt) and hasattr(dropoff_dt, 'to_pydatetime'):
                dropoff_dt = dropoff_dt.to_pydatetime()
                
            values.append((
                int(row.get('VendorID', 0)) if pd.notna(row.get('VendorID')) else None,
                pickup_dt,
                dropoff_dt,
                int(row.get('passenger_count', 0)) if pd.notna(row.get('passenger_count')) else None,
                float(row.get('trip_distance', 0)) if pd.notna(row.get('trip_distance')) else None,
                int(row.get('RatecodeID', 0)) if pd.notna(row.get('RatecodeID')) else None,
                str(row.get('store_and_fwd_flag', '')) if pd.notna(row.get('store_and_fwd_flag')) else None,
                int(row.get('PULocationID', 0)) if pd.notna(row.get('PULocationID')) else None,
                int(row.get('DOLocationID', 0)) if pd.notna(row.get('DOLocationID')) else None,
                int(row.get('payment_type', 0)) if pd.notna(row.get('payment_type')) else None,
                float(row.get('fare_amount', 0)) if pd.notna(row.get('fare_amount')) else None,
                float(row.get('extra', 0)) if pd.notna(row.get('extra')) else None,
                float(row.get('mta_tax', 0)) if pd.notna(row.get('mta_tax')) else None,
                float(row.get('tip_amount', 0)) if pd.notna(row.get('tip_amount')) else None,
                float(row.get('tolls_amount', 0)) if pd.notna(row.get('tolls_amount')) else None,
                float(row.get('improvement_surcharge', 0)) if pd.notna(row.get('improvement_surcharge')) else None,
                float(row.get('total_amount', 0)) if pd.notna(row.get('total_amount')) else None,
                float(row.get('congestion_surcharge', 0)) if pd.notna(row.get('congestion_surcharge')) else None,
                str(row.get('pu_borough', '')) if pd.notna(row.get('pu_borough')) else None,
                str(row.get('pu_zone', '')) if pd.notna(row.get('pu_zone')) else None,
                str(row.get('service_zone', '')) if pd.notna(row.get('service_zone')) else None,
                str(row.get('do_borough', '')) if pd.notna(row.get('do_borough')) else None,
                str(row.get('do_zone', '')) if pd.notna(row.get('do_zone')) else None,
                str(row.get('do_service_zone', '')) if pd.notna(row.get('do_service_zone')) else None,
                float(row.get('duration_mins', 0)) if pd.notna(row.get('duration_mins')) else None,
                float(row.get('avg_speed_mph', 0)) if pd.notna(row.get('avg_speed_mph')) else None,
                float(row.get('tip_percentage', 0)) if pd.notna(row.get('tip_percentage')) else None,
                int(row.get('pickup_hour', 0)) if pd.notna(row.get('pickup_hour')) else None,
                str(row.get('fare_range', '')) if pd.notna(row.get('fare_range')) else None,
                str(row.get('distance_category', '')) if pd.notna(row.get('distance_category')) else None
            ))
        
        # Execute batch insert and commit to database
        cursor.executemany(insert_query, values)
        conn.commit()
        
        # Progress indicator
        progress_pct = (end_idx / total_rows) * 100
        print(f"     Progress: {end_idx:,}/{total_rows:,} records ({progress_pct:.1f}%)")
    
    print(f"   [OK] All trip records inserted successfully! ({total_rows:,} records)")
    
    print("\n   [SUCCESS] Database population complete!")
    print(f"      Database: {DB_CONFIG['database']}")
    print(f"      Trip records: {total_rows:,}")
    print(f"      Zone records: {len(zone_values)}")
    print(f"      Taxi zones: {len(taxi_zones_values)}")
    print(f"      Excluded data log: Ready for tracking")
    
except Error as e:
    print(f"\n   [ERROR] MySQL operation failed")
    print(f"   Details: {e}")
    print("   Please check your database credentials in the .env file")
finally:
    # Always close database connections to free resources
    if cursor:
        cursor.close()
    if conn:
        conn.close()
    print("\n   Database connection closed")


# STEP 6: GEOJSON EXPORT
print("\nSTEP 6: Exporting GeoJSON for mapping...")
print("-" * 70)
print("   > Converting spatial data to GeoJSON format...")
zones_spatial.to_file(GEOJSON_OUT, driver='GeoJSON')
print(f"   [OK] GeoJSON exported to: {GEOJSON_OUT}")

# PIPELINE COMPLETION
print("\n" + "="*70)
print("ETL PIPELINE COMPLETED SUCCESSFULLY")
print("="*70)
print("\nSummary:")
print(f"   - Loaded: {initial_count:,} raw records")
print(f"   - Cleaned: {len(df):,} valid records")
print(f"   - Rejected: {records_removed:,} invalid records")
print(f"   - Database: {DB_CONFIG['database']}")
print(f"   - Tables: trips ({total_rows:,} rows), zones ({len(zone_values)} rows), taxi_zones ({len(taxi_zones_values)} rows)")
print(f"   - GeoJSON: {GEOJSON_OUT}")
print("\nYour data is ready! You can now run app.py to start the API server.")
print("="*70 + "\n")

