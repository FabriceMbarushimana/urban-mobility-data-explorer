# Urban Mobility Data Explorer

A comprehensive data analysis platform for exploring NYC taxi trip patterns using custom algorithms and real-world datasets. This project implements ETL pipelines, custom sorting and outlier detection algorithms, and a RESTful API for analyzing urban transportation data.

**Repository:** [https://github.com/FabriceMbarushimana/urban-mobility-data-explorer](https://github.com/FabriceMbarushimana/urban-mobility-data-explorer)

**Presentetion Video:** [(https://www.loom.com/share/075c3c0de7cf4bb089b595ff64c3b126)]



**Team Participation document:** [[https://docs.google.com/spreadsheets/d/1i1QJRnCEk0WvKSzJFw4rc3uzqN_qys0qObbPB9KV5gk/edit?gid=0#gid=0](https://docs.google.com/spreadsheets/d/1i1QJRnCEk0WvKSzJFw4rc3uzqN_qys0qObbPB9KV5gk/edit?gid=0#gid=0)] 

**Urban Mobility Data Explorer Technical Documentation Report:** [(https://docs.google.com/document/d/1ZbzQAD9_oWcMaw74pwCNP9T42BVXc7MM/edit?usp=sharing&ouid=113359116985828265805&rtpof=true&sd=true)] 

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Technology Stack](#technology-stack)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [API Endpoints](#api-endpoints)
- [File Descriptions](#file-descriptions)
- [Custom Algorithms](#custom-algorithms)
- [Database Schema](#database-schema)
- [Data Sources](#data-sources)
- [Troubleshooting](#troubleshooting)
- [License](#license)

---

## Overview

This project analyzes NYC taxi trip data (Yellow Cab January 2019) to uncover insights about urban mobility patterns. It features:
- **ETL Pipeline**: Loads, cleans, and processes 15,000+ trip records
- **Custom Algorithms**: QuickSort, IQR outlier detection, manual aggregation without libraries
- **RESTful API**: 13 endpoints for querying trip statistics and patterns
- **MySQL Database**: 4-table schema with foreign key relationships and 11 indexes
- **Geospatial Analysis**: Borough-level insights using NYC taxi zone shapefiles with 265 zones

---

## Features

- **Data Processing**
  - ETL pipeline with 6 processing steps
  - Data cleaning (outlier removal, validation)
  - Feature engineering (speed calculation, trip duration, time categorization)
  - Batch database insertion (1000 records/batch)

- **Custom Algorithm Implementations**
  - QuickSort algorithm (O(n log n) average complexity)
  - IQR-based outlier detection
  - Manual hourly aggregation
  - Traffic congestion hour identification

- **Analytics API**
  - 13 RESTful endpoints for comprehensive analysis
  - Summary statistics across entire dataset
  - Hourly and borough-level analysis
  - Route popularity ranking
  - Payment type and tip analysis
  - Speed and fare distribution patterns
  - Weekend vs weekday comparisons

- **Database**
  - MySQL with optimized indexing and foreign key relationships
  - 4 tables: zones (4 columns), taxi_zones (6 columns), trips (30 columns), excluded_data_log (7 columns)
  - 11 indexes for query performance
  - Foreign keys ensuring referential integrity

---

## Project Structure

```
urban-mobility-data-explorer/
├── backend/
│   ├── app.py                      # Flask API server (13 endpoints)
│   ├── database_operations.py      # MySQL database handler
│   ├── main.py                     # ETL pipeline script
│   ├── custom_algorithms.py        # Custom sort/analysis algorithms
│   └── README.md                   # Backend API documentation
├── data/
│   ├── yellow_tripdata_2019-01.csv # NYC taxi trip data (15,000 records)
│   ├── taxi_zone_lookup.csv        # Zone ID to borough mapping (265 zones)
│   ├── taxi_zones.json             # Geographic zone data (265 zones)
│   └── taxi_zones.*                # Shapefile for geospatial analysis
├── Database/
│   └── db_design.sql               # MySQL schema (4 tables with relationships)
├── frontend/                       # (Frontend files - to be added)
├── .env                            # Database credentials (not in repo)
├── .env.example                    # Environment variable template
├── .gitignore                      # Git ignore rules
├── requirements.txt                # Python dependencies
└── README.md                       # This file
```

---

## Technology Stack

**Backend:**
- Python 3.8+
- Flask 3.1.2 (Web framework)
- Flask-CORS 6.0.2 (Cross-origin support)

**Database:**
- MySQL 8.0+
- mysql-connector-python

**Data Processing:**
- pandas 3.0.0 (Data manipulation)
- geopandas 1.1.2 (Geospatial analysis)
- numpy 2.4.2 (Numerical operations)

**Configuration:**
- python-dotenv 1.2.1 (Environment management)

---

## Prerequisites

Before installation, ensure you have:

1. **Python 3.8 or higher**
   ```bash
   python --version
   ```

2. **MySQL Server 8.0 or higher**
   - Download: [https://dev.mysql.com/downloads/mysql/](https://dev.mysql.com/downloads/mysql/)
   - Ensure MySQL service is running

3. **pip** (Python package manager)
   ```bash
   pip --version
   ```

4. **Git** (for cloning the repository)
   ```bash
   git --version
   ```

---

## Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/FabriceMbarushimana/urban-mobility-data-explorer.git
cd urban-mobility-data-explorer
```

### Step 2: Install Python Dependencies

```bash
pip install -r requirements.txt
```

**Dependencies installed:**
- Flask and flask-cors (API server)
- pandas, geopandas, numpy (Data processing)
- PyMySQL, SQLAlchemy (Database connectivity)
- python-dotenv (Environment configuration)
- shapely, pyproj, pyogrio (Geospatial operations)

### Step 3: Set Up MySQL Database

1. **Start MySQL Server**
   ```bash
   # Windows
   net start MySQL80

   # macOS/Linux
   sudo systemctl start mysql
   ```

2. **Create Database**
   ```bash
   mysql -u root -p
   ```
   ```sql
   CREATE DATABASE urban_mobility;
   EXIT;
   ```

3. **Import Schema**
   ```bash
   mysql -u root -p urban_mobility < Database/db_design.sql
   ```

### Step 4: Configure Environment Variables

1. **Create `.env` file** (copy from example):
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` file** with your database credentials:
   ```env
   DB_HOST=localhost
   DB_USER=root
   DB_PASSWORD=your_mysql_password
   DB_NAME=urban_mobility
   DB_PORT=3306
   ```

---

## Configuration

### Environment Variables (.env)

| Variable | Description | Example |
|----------|-------------|---------|
| `DB_HOST` | MySQL server hostname | `localhost` |
| `DB_USER` | MySQL username | `root` |
| `DB_PASSWORD` | MySQL password | `my_secure_password` |
| `DB_NAME` | Database name | `urban_mobility` |
| `DB_PORT` | MySQL port | `3306` |

### API Configuration (app.py)

- **Port**: 5000 (default)
- **Host**: 127.0.0.1
- **CORS Origins**: `http://localhost:5500`, `http://127.0.0.1:5500`
- **Session Lifetime**: 24 hours
- **Debug Mode**: Enabled (disable in production)

---

## Running the Application

### Step 1: Load Data (ETL Pipeline)

Run the ETL script to process and load data into MySQL:

```bash
cd backend
python main.py
```

**What this does:**
1. [LOADING] Reads CSV files (15,000 trip records) + zone lookup (265 zones) + taxi_zones.json (265 zones)
2. [INTEGRATION] Merges trips with zone/borough information
3. [CLEANING] Removes invalid dates, outliers using IQR method (~300-5,000 records rejected)
4. [ENGINEERING] Calculates speed, duration, tip percentage, fare/distance categories
5. [DATABASE] Creates 4 tables with indexes/FKs, inserts zones → taxi_zones → trips
6. [EXPORT] Generates GeoJSON file for mapping

**Expected output:**
```
====================================================================
              NYC TAXI DATA ETL PIPELINE (Sample Mode)
====================================================================
Database: urban_mobility (MySQL)
Sample Size: 15000 rows
====================================================================

STEP 1: Loading data files...
   > Loading taxi trip data (15,000 rows sample)...
   [OK] Loaded 15,000 trip records
   > Loading zone lookup table...
   [OK] Loaded 265 zones
   > Loading taxi zones geographic data...
   [OK] Loaded 265 taxi zones
   > Loading spatial data (shapefiles)...
   [OK] Loaded 265 geographic zones

STEP 2: Integrating datasets...
   > Joining trip data with pickup zone information...
   [OK] Pickup zones merged successfully
   > Joining trip data with dropoff zone information...
   [OK] Dropoff zones merged successfully
   [OK] Final merged dataset: 15,000 records with 35 columns

STEP 3: Cleaning and validating data...
   > Removing invalid dates...
   [OK] Date validation complete: 14,950 records
   > Detecting and removing outliers (IQR method)...
   [OK] Outlier removal complete: 14,684 valid records
   [INFO] Records removed: 316

STEP 4: Feature engineering...
   > Calculating trip duration...
   [OK] Duration calculated
   > Calculating average speed...
   [OK] Speed calculated
   > Creating fare categories...
   [OK] Fare ranges created (4 brackets)
   > Creating distance categories...
   [OK] Distance categories created (5 brackets)
   [INFO] Feature engineering complete: 39 total columns

STEP 5: Loading data into MySQL database...
   > Connecting to MySQL server...
   [OK] Connected to MySQL server at localhost:3306
   > Setting up database 'urban_mobility'...
   [OK] Database 'urban_mobility' ready
   > Dropping existing tables (if any)...
   [OK] Old tables removed (fresh start)
   [OK] Database schema created successfully
        - zones table (4 columns, 2 indexes)
        - taxi_zones table (6 columns, 3 indexes, 1 FK)
        - trips table (30 columns, 6 indexes, 2 FKs)
        - excluded_data_log table (7 columns, 2 indexes)
   
   > Inserting zone lookup data...
   [OK] Zone lookup data inserted (265 zones)
   
   > Inserting taxi zones geographic data...
   [OK] Taxi zones geographic data inserted (265 zones)
   
   > Inserting trip records into database...
     Total records to insert: 14,684
     Progress: 1,000/14,684 records (6.8%)
     Progress: 2,000/14,684 records (13.6%)
     ...
     Progress: 14,684/14,684 records (100.0%)
   [OK] All trip records inserted successfully! (14,684 records)
   
   [SUCCESS] Database population complete!
      Database: urban_mobility
      Trip records: 14,684
      Zone records: 265
      Taxi zones: 265
      Excluded data log: Ready for tracking

STEP 6: Exporting GeoJSON for mapping...
   > Converting spatial data to GeoJSON format...
   [OK] GeoJSON exported to: ../data/taxi_zones.geojson

====================================================================
ETL PIPELINE COMPLETED SUCCESSFULLY
====================================================================
Summary:
   - Loaded: 15,000 raw records
   - Cleaned: 14,684 valid records
   - Rejected: 316 invalid records
   - Database: urban_mobility
   - Tables: trips (14,684 rows), zones (265 rows), taxi_zones (265 rows)
   - GeoJSON: ../data/taxi_zones.geojson

Your data is ready! You can now run app.py to start the API server.
====================================================================
```

### Step 2: Start the API Server

In a new terminal (keep the database running):

```bash
cd backend
python app.py
```

**Expected output:**
```
======================================================================
                URBAN MOBILITY EXPLORER API (MySQL)
======================================================================
Database: MySQL - urban_mobility
API URL: http://127.0.0.1:5000
Authentication: DISABLED (No login required)
======================================================================

 Server starting...
Keep this terminal open while using the app!
Press CTRL+C to stop the server
======================================================================

 * Running on http://127.0.0.1:5000
```

### Step 3: Test the API

Open your browser or use curl:

```bash
# Status check
curl http://127.0.0.1:5000/api/status

# Get summary statistics
curl http://127.0.0.1:5000/api/stats/summary

# Get trips (first 10)
curl http://127.0.0.1:5000/api/trips/list?limit=10
```

---

## API Endpoints

### Base URL
```
http://127.0.0.1:5000
```

### Health & Status

#### `GET /api/status`
**Description:** Status check endpoint  
**Returns:**
```json
{
  "status": "healthy",
  "service": "Urban Mobility Explorer API"
}
```

---

### Statistics Endpoints

#### `GET /api/stats/summary`
**Description:** Overall dataset summary statistics  
**Returns:**
```json
{
  "total_trips": 10234,
  "avg_fare": 12.45,
  "avg_distance": 2.87,
  "avg_duration": 13.5,
  "total_revenue": 127543.20,
  "avg_passengers": 1.6
}
```

---

### Trip Data Endpoints

#### `GET /api/trips/list`
**Description:** Get trips with filtering and pagination  
**Query Parameters:**
| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `limit` | int | Records to return | 100 |
| `offset` | int | Records to skip | 0 |
| `borough` | string | Filter by borough | None |
| `min_fare` | float | Minimum fare | None |
| `max_fare` | float | Maximum fare | None |
| `min_distance` | float | Minimum distance | None |
| `max_distance` | float | Maximum distance | None |
| `start_date` | string | Start date (YYYY-MM-DD) | None |
| `end_date` | string | End date (YYYY-MM-DD) | None |
| `hour` | int | Hour of day (0-23) | None |
| `is_weekend` | bool | Weekend filter | None |

**Example Request:**
```bash
curl "http://127.0.0.1:5000/api/trips/list?borough=Manhattan&limit=5&min_fare=10"
```

**Returns:**
```json
{
  "trips": [
    {
      "id": 1,
      "pickup_datetime": "2019-01-01 00:46:40",
      "dropoff_datetime": "2019-01-01 00:53:20",
      "passenger_count": 1,
      "trip_distance": 1.5,
      "fare_amount": 7.0,
      "tip_amount": 1.65,
      "total_amount": 11.15,
      "pu_borough": "Manhattan",
      "do_borough": "Manhattan",
      "duration_mins": 6.67,
      "avg_speed_mph": 13.5
    }
  ]
}
```

---

### Analysis Endpoints

#### `GET /api/analysis/hourly-patterns`
**Description:** Trip patterns by hour of day  
**Returns:**
```json
[
  {
    "hour": 0,
    "trip_count": 245,
    "avg_fare": 11.23,
    "avg_distance": 2.1,
    "avg_speed": 18.5
  }
]
```

#### `GET /api/analysis/borough`
**Description:** Analysis by NYC borough  
**Returns:**
```json
{
  "pickup": [
    {
      "borough": "Manhattan",
      "trip_count": 7543,
      "avg_fare": 13.45,
      "avg_distance": 2.3
    }
  ],
  "dropoff": [ /* similar structure */ ]
}
```

#### `GET /api/analysis/fare-distribution`
**Description:** Fare amount distribution  
**Returns:**
```json
[
  {
    "fare_range": "$0-$10",
    "trip_count": 3421,
    "percentage": 33.4
  }
]
```

#### `GET /api/analysis/distance`
**Description:** Distance-based insights  
**Returns:**
```json
{
  "avg_distance": 2.87,
  "total_distance": 29378.5,
  "distance_categories": [
    {
      "category": "short",
      "count": 6543,
      "percentage": 63.9
    }
  ]
}
```

#### `GET /api/analysis/payment`
**Description:** Payment type distribution  
**Returns:**
```json
[
  {
    "payment_type": 1,
    "payment_name": "Credit Card",
    "trip_count": 7234,
    "percentage": 70.7
  }
]
```

#### `GET /api/analysis/speed`
**Description:** Average speed by hour  
**Returns:**
```json
[
  {
    "hour": 0,
    "avg_speed_mph": 18.5,
    "trip_count": 245
  }
]
```

#### `GET /api/analysis/tips`
**Description:** Tip percentage analysis  
**Returns:**
```json
{
  "avg_tip_percentage": 18.5,
  "avg_tip_amount": 2.34,
  "trips_with_tips": 7234,
  "tip_ranges": [ /* distribution data */ ]
}
```

#### `GET /api/analysis/weekend-comparison`
**Description:** Weekend vs weekday patterns  
**Returns:**
```json
{
  "weekday": {
    "trip_count": 7234,
    "avg_fare": 12.45
  },
  "weekend": {
    "trip_count": 3000,
    "avg_fare": 13.21
  }
}
```

---

### Route Endpoints

#### `GET /api/routes/top`
**Description:** Most popular routes (uses custom QuickSort)  
**Query Parameters:**
| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `limit` | int | Top N routes | 10 |

**Returns:**
```json
[
  {
    "pickup_zone": "Times Square",
    "dropoff_zone": "Penn Station",
    "trip_count": 456,
    "avg_fare": 8.50,
    "avg_distance": 1.2
  }
]
```

---

### Custom Insights Endpoints

#### `GET /api/insights/custom`
**Description:** Custom algorithm analysis (outliers, aggregation)  
**Returns:**
```json
{
  "outliers_detected": 127,
  "hourly_aggregation": [
    {
      "hour": 0,
      "total_trips": 245,
      "total_revenue": 2876.45
    }
  ],
  "outlier_samples": [
    {
      "id": 1234,
      "fare_amount": 125.50,
      "reason": "fare_outlier"
    }
  ]
}
```

---

## File Descriptions

### Backend Files

#### `backend/app.py` (352 lines)
**Purpose:** Flask API server with RESTful endpoints  
**Key Components:**
- Flask application initialization with CORS support
- 13 API endpoints organized by category (stats, trips, analysis, routes, insights)
- Session management configuration
- Error handlers (404, 500)
- Database handler integration
- Custom algorithm implementations (CustomSort, OutlierDetector, TripAggregator)

**API Endpoints (13 total):**
1. `/api/status` - Health check
2. `/api/stats/summary` - Overall statistics
3. `/api/trips/list` - Filtered trip listing
4. `/api/analysis/hourly-patterns` - Hour-based analysis
5. `/api/analysis/borough` - Borough comparison
6. `/api/analysis/fare-distribution` - Fare brackets
7. `/api/analysis/distance` - Distance insights
8. `/api/analysis/payment` - Payment types
9. `/api/analysis/speed` - Speed by hour
10. `/api/analysis/tips` - Tipping patterns
11. `/api/analysis/weekend-comparison` - Weekend vs weekday
12. `/api/routes/top` - Popular routes (QuickSort)
13. `/api/insights/custom` - Custom algorithms (IQR outliers)

---

#### `backend/database_operations.py`
**Purpose:** MySQL database interface and query handler  
**Key Components:**
- `DatabaseHandler` class with connection management
- 13 query methods matching API endpoints
- Environment variable configuration (.env)
- Error handling and connection pooling
- Support for complex filtering and pagination

**Key Methods:**
- `get_summary_stats()`: Overall statistics
- `get_trips()`: Filtered trip retrieval with 10 filter options
- `get_hourly_patterns()`: Time-based analysis
- `get_borough_analysis()`: Location-based insights
- `get_fare_distribution()`: Fare bracket analysis
- `get_distance_analysis()`: Distance patterns
- `get_top_routes()`: Popular route identification
- `get_payment_analysis()`: Payment method breakdown
- `get_speed_analysis()`: Speed by hour
- `get_tip_analysis()`: Tipping patterns
- `get_weekend_comparison()`: Weekday vs weekend stats
- `get_trips_for_analysis()`: Raw data for custom algorithms

---
 (539 lines)
**Purpose:** ETL pipeline for data loading and preprocessing  
**Key Components:**
- **Step 1: Data Loading** - Reads CSV (15k trips), zone lookup (265 zones), taxi_zones.json (265 zones), shapefiles
- **Step 2: Data Integration** - Merges trips with zone/borough info
- **Step 3: Data Cleaning** - Removes invalid dates, outliers using IQR method
- **Step 4: Feature Engineering** - Calculates speed, duration, tip %, categories
- **Step 5: Database Loading** - Creates 4 tables, inserts zones → taxi_zones → trips in correct order
- **Step 6: GeoJSON Export** - Creates geospatial file for mapping

**Database Operations:**
- Creates `zones`, `taxi_zones`, `trips`, `excluded_data_log` tables with all indexes and foreign keys
- Inserts 265 zone records
- Inserts 265 taxi_zones geographic records
- Batch inserts ~10,000-14,000 trip records (1000 rows/batch)
- Validates foreign key constraints

**Processing Details:**
- Sample mode: 15,000 trips (configurable via `nrows` parameter)
- Data quality: ~10,000-14,000 clean records after filtering
- Rejection rate: ~300-5,000 invalid records removed
- Batch size: 1000 records per MySQL insert
- Validation: Date checks, numeric validation, IQR
- Validation: Date checks, numeric validation, outlier removal

---

#### `backend/custom_algorithms.py`
**Purpose:** Custom algorithm implementations demonstrating CS fundamentals  
**Key Components:**

1. **CustomSort Class**
   - QuickSort implementation (O(n log n) average)
   - Partition-based divide and conquer
   - Used for ranking top routes
   
2. **OutlierDetector Class**
   - IQR (Interquartile Range) method
   - Bubble sort for quartile calculation (O(n²))
   - Detects fare, distance, and duration anomalies
   
3. **TripAggregator Class**
   - Manual hourly aggregation without pandas groupby
   - Linear time complexity (O(n))
   - Accumulates totals and calculates averages
   
4. **SpeedAnalyzer Class**
   - Identifies congestion hours
   - Analyzes speed patterns by time of day
   - Linear scan algorithm (O(n))

---

### Data Files

#### `data/yellow_tripdata_2019-01.csv`
**Description:** NYC Yellow Taxi trip data (January 2019)  
**Records:** 15,000 (sample) from full dataset  
**Columns:** 18 fields including pickup/dropoff times, locations, fares, tips  
**Source:** [NYC Taxi & Limousine Commission](https://www1.nyc.gov/site/tlc/about/tlc-trip-record-data.page)

#### `data/taxi_zone_lookup.csv`
**Description:** Zone ID to borough/neighborhood mapping  
**Records:** 265 taxi zones across NYC  
**Columns:** LocationID, Borough, Zone, service_zone

#### `data/taxi_zones.shp` (+ .shx, .dbf, .prj, etc.)
**Description:** Shapefile for geospatial visualization  
**Format:** ESRI Shapefile  
**Usage:** Borough boundary mapping, zone visualization

---

### Database Files

#### `Database/db_design.sql`
**Description:** MySQL schema definition  
**Tables:**
1. **trips** (30 columns)
   - Core fields: datetime, location IDs, fares, passenger count
   - Enriched fields: borough names, speed, duration, categories
   - Primary key: `id` (auto-increment)
   
2. **zones** (4 columns)
   - LocationID, Borough, Zone, service_zone
   - Primary key: `LocationID`

---

### Configuration Files

#### `.env` (Not in repository)
**Description:** Database credentials (create from .env.example)  
**Contents:**
```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=urban_mobility
DB_PORT=3306
```

#### `.env.example`
**Description:** Template for environment variables  
**Purpose:** Shows required configuration without exposing secrets

#### `requirements.txt`
**Description:** Python package dependencies  
**Packages:** 23 packages including Flask, pandas, geopandas, PyMySQL

#### `.gitignore`
**Description:** Files excluded from version control  
**Includes:**
- `.env` (credentials)
- `__pycache__/` (Python cache)
- `*.pyc` (compiled Python)
- `processed/` (output files)
- `.vscode/` (editor config)
- `taxi_zones.geojson` (generated file)

---

## Custom Algorithms

This project implements several algorithms from scratch without using built-in library functions:

### 1. QuickSort Algorithm (`CustomSort`)
**File:** `custom_algorithms.py`  
**Purpose:** Sort routes by trip count for ranking  
**Complexity:** O(n log n) average, O(n²) worst case  
**Implementation:**
- Pivot selection
- Partition-based divide and conquer
- Recursive sorting

**Usage:**
```python
sorter = CustomSort()
sorted_routes = sorter.sort_by_trip_count(routes)
```

### 2. IQR Outlier Detection (`OutlierDetector`)
**File:** `custom_algorithms.py`  
**Purpose:** Identify anomalous fares, distances, durations  
**Method:** Interquartile Range (IQR)  
**Complexity:** O(n²) due to bubble sort  
**Process:**
1. Sort data using bubble sort
2. Calculate Q1 (25th percentile) and Q3 (75th percentile)
3. Compute IQR = Q3 - Q1
4. Flag values outside [Q1 - 1.5*IQR, Q3 + 1.5*IQR]

**Usage:**
```python
detector = OutlierDetector()
outliers = detector.detect_fare_outliers(trips)
```

### 3. Manual Aggregation (`TripAggregator`)
**File:** `custom_algorithms.py`  
**Purpose:** Aggregate trips by hour without pandas groupby  
**Complexity:** O(n) linear  
**Process:**
1. Initialize accumulator dictionary
2. Iterate through trips once
3. Sum totals and count trips per hour
4. Calculate averages

**Usage:**
```python
aggregator = TripAggregator()
hourly_data = aggregator.aggregate_by_hour(trips)
```

### 4. Congestion Hour Analyzer (`SpeedAnalyzer`)
**File:** `custom_algorithms.py`  
**Purpose:** Find hours with slowest average speeds  
**Complexity:** O(n) linear  
**Process:**
1. Group speeds by hour
2. Calculate average speed per hour
3. Identify hours below threshold

**Usage:**
```python
analyzer = SpeedAnalyzer()
congestion_hours = analyzer.find_congestion_hours(trips)
```

---

## Database Schema

The database consists of 4 tables with **11 indexes** and **3 foreign key relationships** ensuring data integrity and query performance.

### Overview

| Table | Columns | Indexes | FKs | Purpose |
|-------|---------|---------|-----|---------|
| `zones` | 4 | 2 | 0 | NYC taxi zone lookup (265 zones) |
| `taxi_zones` | 6 | 3 | 1 | Geographic zone data with shapes |
| `trips` | 30 | 6 | 2 | Main trip records (~10k-15k records) |
| `excluded_data_log` | 7 | 2 | 0 | ETL data quality tracking |

---

### `zones` Table (4 columns, 2 indexes)

**Purpose:** Reference table mapping zone IDs to boroughs and neighborhoods (265 zones)

| Column | Type | Description |
|--------|------|-------------|
| `LocationID` | INT | Primary key, zone identifier (1-265) |
| `Borough` | VARCHAR(50) | NYC borough name (Manhattan, Brooklyn, etc.) |
| `Zone` | VARCHAR(100) | Neighborhood/zone name |
| `service_zone` | VARCHAR(50) | Service zone classification |

**Indexes:**
- `idx_borough` on `Borough`
- `idx_zone` on `Zone`

---

### `taxi_zones` Table (6 columns, 3 indexes, 1 FK)

**Purpose:** Geographic zone information with shape measurements from GIS data

| Column | Type | Description |
|--------|------|-------------|
| `objectid` | INT | Primary key, GIS object identifier |
| `shape_leng` | DECIMAL(15,10) | Zone perimeter length |
| `shape_area` | DECIMAL(15,10) | Zone area |
| `zone` | VARCHAR(100) | Zone name |
| `locationid` | INT | Foreign key to `zones.LocationID` |
| `borough` | VARCHAR(50) | Borough name |

**Indexes:**
- `idx_locationid` on `locationid`
- `idx_borough` on `borough`
- `idx_zone` on `zone`

**Foreign Keys:**
- `locationid` → `zones(LocationID)` ON DELETE CASCADE

---

### `trips` Table (30 columns, 6 indexes, 2 FKs)

**Purpose:** Main trip records with original TLC data + calculated features

| Column | Type | Description |
|--------|------|-------------|
| `id` | INT | Primary key (auto-increment) |
| `VendorID` | INT | Cab company identifier (1=Creative, 2=VeriFone) |
| `tpep_pickup_datetime` | DATETIME | Pickup timestamp |
| `tpep_dropoff_datetime` | DATETIME | Dropoff timestamp |
| `passenger_count` | INT | Number of passengers |
| `trip_distance` | FLOAT | Distance in miles |
| `RatecodeID` | INT | Rate code (1=Standard, 2=JFK, etc.) |
| `store_and_fwd_flag` | VARCHAR(10) | Trip record stored locally (Y/N) |
| `PULocationID` | INT | Pickup location zone ID (FK to zones) |
| `DOLocationID` | INT | Dropoff location zone ID (FK to zones) |
| `payment_type` | INT | Payment method (1=Card, 2=Cash) |
| `fare_amount` | FLOAT | Metered fare ($) |
| `extra` | FLOAT | Extra charges ($) |
| `mta_tax` | FLOAT | MTA tax ($0.50) |
| `tip_amount` | FLOAT | Tip amount ($) |
| `tolls_amount` | FLOAT | Tolls ($) |
| `improvement_surcharge` | FLOAT | Surcharge fee ($0.30) |
| `total_amount` | FLOAT | Total charge ($) |
| `congestion_surcharge` | FLOAT | Congestion fee ($) |
| `pu_borough` | VARCHAR(50) | Pickup borough name |
| `pu_zone` | VARCHAR(100) | Pickup zone name |
| `service_zone` | VARCHAR(50) | Service zone type |
| `do_borough` | VARCHAR(50) | Dropoff borough name |
| `do_zone` | VARCHAR(100) | Dropoff zone name |
| `do_service_zone` | VARCHAR(50) | Dropoff service zone |
| `duration_mins` | FLOAT | **Calculated:** Trip duration |
| `avg_speed_mph` | FLOAT | **Calculated:** Average speed |
| `tip_percentage` | FLOAT | **Calculated:** Tip as % of fare |
| `pickup_hour` | INT | **Calculated:** Hour of pickup (0-23) |
| `fare_range` | VARCHAR(20) | **Calculated:** Fare category |
| `distance_category` | VARCHAR(20) | **Calculated:** Distance category |

**Indexes:**
- `idx_pickup_location` on `PULocationID`
- `idx_dropoff_location` on `DOLocationID`
- `idx_pickup_datetime` on `tpep_pickup_datetime`
- `idx_pickup_hour` on `pickup_hour`
- `idx_pu_borough` on `pu_borough`
- `idx_do_borough` on `do_borough`

**Foreign Keys:**
- `PULocationID` → `zones(LocationID)` ON DELETE SET NULL
- `DOLocationID` → `zones(LocationID)` ON DELETE SET NULL

---

### `excluded_data_log` Table (7 columns, 2 indexes)

**Purpose:** Audit trail for data quality issues and rejected records during ETL

| Column | Type | Description |
|--------|------|-------------|
| `log_id` | INT | Primary key (auto-increment) |
| `issue_type` | VARCHAR(50) | Type of issue (date_invalid, outlier, etc.) |
| `trip_identifier` | VARCHAR(255) | Reference to problematic trip |
| `field_name` | VARCHAR(50) | Field with issue |
| `issue_description` | TEXT | Detailed description |
| `action_taken` | VARCHAR(100) | Action performed (excluded, flagged) |
| `logged_at` | TIMESTAMP | Timestamp of logging |

**Indexes:**
- `idx_issue_type` on `issue_type`
- `idx_logged_at` on `logged_at`

**Use Cases:**
- Data quality monitoring
- ETL debugging
- Compliance auditing
- Data lineage tracking

---

## Data Sources

### NYC Taxi & Limousine Commission (TLC)
**Dataset:** Yellow Taxi Trip Records (January 2019)  
**URL:** [https://www1.nyc.gov/site/tlc/about/tlc-trip-record-data.page](https://www1.nyc.gov/site/tlc/about/tlc-trip-record-data.page)  
**License:** Public domain (NYC Open Data)

**Dataset Details:**
- **Records:** 7.7 million trips (full month), 15,000 sample used
- **Date Range:** January 1-31, 2019
- **File Format:** CSV
- **Size:** ~700 MB (full), ~2 MB (sample)

### NYC Taxi Zones Shapefile
**Source:** NYC TLC  
**Format:** ESRI Shapefile  
**Zones:** 265 taxi zones across 5 boroughs  
**Usage:** Geospatial visualization and borough mapping

---

## Troubleshooting

### Common Issues

#### 1. MySQL Connection Error
**Error:** `Can't connect to MySQL server`

**Solution:**
- Verify MySQL service is running
- Check credentials in `.env` file
- Ensure database `urban_mobility` exists
- Test connection:
  ```bash
  mysql -u root -p -e "SHOW DATABASES;"
  ```

#### 2. Port Already in Use
**Error:** `Address already in use: 5000`

**Solution:**
- Kill process using port 5000:
  ```bash
  # Windows
  netstat -ano | findstr :5000
  taskkill /PID <PID> /F

  # macOS/Linux
  lsof -ti:5000 | xargs kill -9
  ```
- Or change port in `app.py`:
  ```python
  app.run(debug=True, host='127.0.0.1', port=5001)
  ```

#### 3. Module Not Found Error
**Error:** `ModuleNotFoundError: No module named 'flask'`

**Solution:**
- Reinstall dependencies:
  ```bash
  pip install -r requirements.txt
  ```
- Use virtual environment:
  ```bash
  python -m venv venv
  source venv/bin/activate  # macOS/Linux
  venv\Scripts\activate     # Windows
  pip install -r requirements.txt
  ```

#### 4. Empty Database After ETL
**Error:** No records in database after running `main.py`

**Solution:**
- Check if CSV files exist in `data/` folder
- Verify CSV file has data:
  ```bash
  head data/yellow_tripdata_2019-01.csv
  ```
- Check ETL output for errors
- Ensure sample size is sufficient in `main.py`:
  ```python
  SAMPLE_SIZE = 15000
  ```

#### 5. CORS Error in Frontend
**Error:** `Access-Control-Allow-Origin` error

**Solution:**
- Verify CORS configuration in `app.py`:
  ```python
  CORS(app, supports_credentials=True, origins=['http://127.0.0.1:5500'])
  ```
- Add your frontend URL to origins list
- Clear browser cache

#### 6. Slow API Response
**Issue:** API endpoints taking too long

**Solution:**
- Add database indexes:
  ```sql
  CREATE INDEX idx_borough ON trips(pu_borough);
  CREATE INDEX idx_hour ON trips(pickup_hour);
  CREATE INDEX idx_datetime ON trips(tpep_pickup_datetime);
  ```
- Reduce `limit` in API calls
- Use pagination for large datasets

---

## Development Workflow

### Making Changes

1. **Add New API Endpoint:**
   - Add route in `backend/app.py`
   - Add corresponding method in `backend/database_operations.py`
   - Test with curl or Postman

2. **Modify ETL Pipeline:**
   - Edit `backend/main.py`
   - Run pipeline: `python main.py`
   - Verify data in MySQL

3. **Add Custom Algorithm:**
   - Implement in `backend/custom_algorithms.py`
   - Import in `app.py`
   - Call from endpoint

### Testing

```bash
# Test API status
curl http://127.0.0.1:5000/api/status

# Test summary stats
curl http://127.0.0.1:5000/api/stats/summary

# Test with filters
curl "http://127.0.0.1:5000/api/trips/list?borough=Manhattan&limit=5"

# Test custom algorithms
curl http://127.0.0.1:5000/api/insights/custom
```

---
# urban-mobility-data-explorer
