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

