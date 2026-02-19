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
