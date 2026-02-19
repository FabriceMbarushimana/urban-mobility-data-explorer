# Urban Mobility Explorer - Backend API Documentation

Complete documentation for the Urban Mobility Explorer RESTful API.

---

## Table of Contents

- [Overview](#overview)
- [Getting Started](#getting-started)
- [Base URL](#base-url)
- [Response Format](#response-format)
- [Error Handling](#error-handling)
- [API Endpoints](#api-endpoints)
  - [Status Check](#status-check)
  - [Statistics](#statistics)
  - [Trip Data](#trip-data)
  - [Analysis](#analysis)
  - [Routes](#routes)
  - [Custom Insights](#custom-insights)
- [Data Models](#data-models)
- [Filtering & Pagination](#filtering--pagination)
- [Examples](#examples)

---

## Overview

The Urban Mobility Explorer API provides access to NYC taxi trip data analytics. This API offers:

- **13 endpoints** for comprehensive data analysis
- **RESTful design** with JSON responses
- **Flexible filtering** by borough, fare, distance, time, and more
- **Pagination support** for large datasets
- **Custom algorithms** for advanced insights (QuickSort, IQR outlier detection)
- **4-table database** with foreign key relationships and comprehensive indexing

**Technology Stack:**
- Flask 3.1.2 (Python web framework)
- MySQL 8.0+ (Database)
- Flask-CORS (Cross-origin support)

---

## Getting Started

### Prerequisites

1. **MySQL Server** running with `urban_mobility` database
2. **Python 3.8+** with dependencies installed
3. **Environment variables** configured in `.env` file

### Start the Server

```bash
cd backend
python app.py
```

The server will start on `http://127.0.0.1:5000`

### Quick Test

```bash
curl http://127.0.0.1:5000/api/status
```

Expected response:
```json
{
  "status": "healthy",
  "service": "Urban Mobility Explorer API"
}
```

---

## Base URL

```
http://127.0.0.1:5000
```

All endpoints are relative to this base URL.

**Development:** `http://127.0.0.1:5000`  
**Production:** Update to your production domain

---

 

## Response Format

All responses are returned in JSON format.

### Success Response

```json
{
  "data": { /* response data */ }
}
```

### Error Response

```json
{
  "error": "Error message description"
}
```

**HTTP Status Codes:**
- `200` - Success
- `404` - Endpoint not found
- `500` - Internal server error

---

## Error Handling

### Common Errors

**404 - Route Not Found**
```json
{
  "error": "Route not found"
}
```

**500 - Internal Server Error**
```json
{
  "error": "Database connection failed"
}
```

**Invalid Parameters**
```json
{
  "error": "invalid literal for int() with base 10: 'abc'"
}
```

---

## API Endpoints

### Status Check

#### `GET /api/status`

Check if the API server is running and healthy.

**Parameters:** None

**Response:**
```json
{
  "status": "healthy",
  "service": "Urban Mobility Explorer API"
}
```

**Example:**
```bash
curl http://127.0.0.1:5000/api/status
```

---

### Statistics

#### `GET /api/stats/summary`

Get overall summary statistics for the entire dataset.

**Parameters:** None

**Response Fields:**
| Field | Type | Description |
|-------|------|-------------|
| `total_trips` | int | Total number of trips |
| `avg_fare` | float | Average fare amount ($) |
| `avg_distance` | float | Average trip distance (miles) |
| `avg_duration` | float | Average trip duration (minutes) |
| `total_revenue` | float | Sum of all fares ($) |
| `avg_passengers` | float | Average passengers per trip |
| `avg_tip` | float | Average tip amount ($) |
| `avg_speed` | float | Average speed (mph) |

**Example Response:**
```json
{
  "total_trips": 10234,
  "avg_fare": 12.45,
  "avg_distance": 2.87,
  "avg_duration": 13.54,
  "total_revenue": 127543.20,
  "avg_passengers": 1.62,
  "avg_tip": 2.15,
  "avg_speed": 12.7
}
```

**Example:**
```bash
curl http://127.0.0.1:5000/api/stats/summary
```

---

### Trip Data

#### `GET /api/trips/list`

Retrieve trip records with optional filtering and pagination.

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | int | 100 | Number of records to return (max recommended: 1000) |
| `offset` | int | 0 | Number of records to skip (for pagination) |
| `borough` | string | null | Filter by NYC borough (Manhattan, Brooklyn, Queens, Bronx, Staten Island) |
| `min_fare` | float | null | Minimum fare amount ($) |
| `max_fare` | float | null | Maximum fare amount ($) |
| `min_distance` | float | null | Minimum trip distance (miles) |
| `max_distance` | float | null | Maximum trip distance (miles) |
| `start_date` | string | null | Start date filter (YYYY-MM-DD format) |
| `end_date` | string | null | End date filter (YYYY-MM-DD format) |
| `hour` | int | null | Filter by hour of day (0-23) |
| `is_weekend` | bool | null | Filter weekend trips (true/false) |

**Response Structure:**
```json
{
  "trips": [
    {
      "id": 1,
      "VendorID": 1,
      "tpep_pickup_datetime": "2019-01-01 00:46:40",
      "tpep_dropoff_datetime": "2019-01-01 00:53:20",
      "passenger_count": 1,
      "trip_distance": 1.5,
      "fare_amount": 7.0,
      "tip_amount": 1.65,
      "total_amount": 11.15,
      "pu_borough": "Manhattan",
      "pu_zone": "East Harlem North",
      "do_borough": "Manhattan",
      "do_zone": "Upper East Side North",
      "duration_mins": 6.67,
      "avg_speed_mph": 13.5,
      "tip_percentage": 23.57,
      "pickup_hour": 0,
      "fare_range": "$5-$15",
      "distance_category": "short"
    }
  ]
}
```

**Examples:**

1. Get first 10 trips:
```bash
curl "http://127.0.0.1:5000/api/trips/list?limit=10"
```

2. Get Manhattan trips with fare $10-$20:
```bash
curl "http://127.0.0.1:5000/api/trips/list?borough=Manhattan&min_fare=10&max_fare=20&limit=50"
```

3. Get trips during rush hour (8 AM):
```bash
curl "http://127.0.0.1:5000/api/trips/list?hour=8&limit=100"
```

4. Get weekend trips:
```bash
curl "http://127.0.0.1:5000/api/trips/list?is_weekend=true&limit=50"
```

5. Pagination example (page 2, 50 per page):
```bash
curl "http://127.0.0.1:5000/api/trips/list?limit=50&offset=50"
```

---

### Analysis

#### `GET /api/analysis/hourly-patterns`

Get trip patterns aggregated by hour of day (0-23).

**Parameters:** None

**Response Structure:**
```json
[
  {
    "hour": 0,
    "trip_count": 245,
    "avg_fare": 11.23,
    "avg_distance": 2.1,
    "avg_speed": 18.5,
    "total_revenue": 2751.35
  },
  {
    "hour": 1,
    "trip_count": 189,
    "avg_fare": 10.87,
    "avg_distance": 1.9,
    "avg_speed": 17.2,
    "total_revenue": 2054.43
  }
]
```

**Use Cases:**
- Identify peak hours
- Analyze demand patterns
- Traffic speed analysis by time

**Example:**
```bash
curl http://127.0.0.1:5000/api/analysis/hourly-patterns
```

---

#### `GET /api/analysis/borough`

Get analysis grouped by NYC borough for both pickup and dropoff locations.

**Parameters:** None

**Response Structure:**
```json
{
  "pickup": [
    {
      "borough": "Manhattan",
      "trip_count": 7543,
      "avg_fare": 13.45,
      "avg_distance": 2.34,
      "total_revenue": 101453.35
    },
    {
      "borough": "Brooklyn",
      "trip_count": 1234,
      "avg_fare": 12.10,
      "avg_distance": 3.21,
      "total_revenue": 14931.40
    }
  ],
  "dropoff": [
    {
      "borough": "Manhattan",
      "trip_count": 7321,
      "avg_fare": 13.21,
      "avg_distance": 2.28,
      "total_revenue": 96731.41
    }
  ]
}
```

**Use Cases:**
- Compare boroughs
- Identify high-demand areas
- Revenue analysis by location

**Example:**
```bash
curl http://127.0.0.1:5000/api/analysis/borough
```

---

#### `GET /api/analysis/fare-distribution`

Get distribution of trips across fare brackets.

**Parameters:** None

**Response Structure:**
```json
[
  {
    "fare_range": "$0-$5",
    "trip_count": 1234,
    "percentage": 12.06,
    "total_revenue": 4567.89
  },
  {
    "fare_range": "$5-$10",
    "trip_count": 3421,
    "percentage": 33.43,
    "total_revenue": 25678.43
  },
  {
    "fare_range": "$10-$15",
    "trip_count": 2876,
    "percentage": 28.11,
    "total_revenue": 35432.21
  },
  {
    "fare_range": "$15+",
    "trip_count": 2703,
    "percentage": 26.41,
    "total_revenue": 61865.67
  }
]
```

**Fare Ranges:**
- `$0-$5` - Very short trips
- `$5-$10` - Short trips
- `$10-$15` - Medium trips
- `$15+` - Long trips

**Example:**
```bash
curl http://127.0.0.1:5000/api/analysis/fare-distribution
```

---

#### `GET /api/analysis/distance`

Get distance-based insights and patterns.

**Parameters:** None

**Response Structure:**
```json
{
  "avg_distance": 2.87,
  "total_distance": 29378.54,
  "max_distance": 18.5,
  "min_distance": 0.1,
  "distance_categories": [
    {
      "category": "short",
      "description": "0-2 miles",
      "count": 6543,
      "percentage": 63.94
    },
    {
      "category": "medium",
      "description": "2-5 miles",
      "count": 2876,
      "percentage": 28.11
    },
    {
      "category": "long",
      "description": "5+ miles",
      "count": 815,
      "percentage": 7.96
    }
  ]
}
```

**Distance Categories:**
- **Short:** 0-2 miles
- **Medium:** 2-5 miles
- **Long:** 5+ miles

**Example:**
```bash
curl http://127.0.0.1:5000/api/analysis/distance
```

---

#### `GET /api/analysis/payment`

Get payment type distribution and patterns.

**Parameters:** None

**Response Structure:**
```json
[
  {
    "payment_type": 1,
    "payment_name": "Credit Card",
    "trip_count": 7234,
    "percentage": 70.68,
    "avg_fare": 13.21,
    "avg_tip": 2.45
  },
  {
    "payment_type": 2,
    "payment_name": "Cash",
    "trip_count": 2543,
    "percentage": 24.85,
    "avg_fare": 11.54,
    "avg_tip": 0.0
  },
  {
    "payment_type": 3,
    "payment_name": "No Charge",
    "trip_count": 321,
    "percentage": 3.14,
    "avg_fare": 0.0,
    "avg_tip": 0.0
  }
]
```

**Payment Types:**
- `1` - Credit Card
- `2` - Cash
- `3` - No Charge
- `4` - Dispute
- `5` - Unknown
- `6` - Voided trip

**Example:**
```bash
curl http://127.0.0.1:5000/api/analysis/payment
```

---

#### `GET /api/analysis/speed`

Get average speed analysis by hour of day.

**Parameters:** None

**Response Structure:**
```json
[
  {
    "hour": 0,
    "avg_speed_mph": 18.54,
    "trip_count": 245,
    "speed_category": "fast"
  },
  {
    "hour": 8,
    "avg_speed_mph": 8.21,
    "trip_count": 876,
    "speed_category": "slow"
  },
  {
    "hour": 17,
    "avg_speed_mph": 7.65,
    "trip_count": 1234,
    "speed_category": "slow"
  }
]
```

**Speed Categories:**
- **Fast:** 15+ mph (low traffic)
- **Normal:** 10-15 mph (moderate traffic)
- **Slow:** < 10 mph (congested)

**Use Cases:**
- Traffic congestion analysis
- Rush hour identification
- Route optimization

**Example:**
```bash
curl http://127.0.0.1:5000/api/analysis/speed
```

---

#### `GET /api/analysis/tips`

Get tip percentage analysis and tipping patterns.

**Parameters:** None

**Response Structure:**
```json
{
  "avg_tip_percentage": 18.54,
  "avg_tip_amount": 2.34,
  "trips_with_tips": 7234,
  "trips_without_tips": 3000,
  "tip_percentage_distribution": [
    {
      "range": "0%",
      "count": 3000,
      "percentage": 29.31
    },
    {
      "range": "10-15%",
      "count": 1234,
      "percentage": 12.06
    },
    {
      "range": "15-20%",
      "count": 3421,
      "percentage": 33.43
    },
    {
      "range": "20-25%",
      "count": 1876,
      "percentage": 18.34
    },
    {
      "range": "25%+",
      "count": 703,
      "percentage": 6.87
    }
  ]
}
```

**Use Cases:**
- Tipping behavior analysis
- Payment method correlation
- Service quality insights

**Example:**
```bash
curl http://127.0.0.1:5000/api/analysis/tips
```

---

#### `GET /api/analysis/weekend-comparison`

Compare weekend vs weekday trip patterns.

**Parameters:** None

**Response Structure:**
```json
{
  "weekday": {
    "trip_count": 7234,
    "avg_fare": 12.45,
    "avg_distance": 2.67,
    "avg_speed": 11.23,
    "total_revenue": 90063.30,
    "avg_tip_percentage": 17.89
  },
  "weekend": {
    "trip_count": 3000,
    "avg_fare": 13.21,
    "avg_distance": 3.12,
    "avg_speed": 13.54,
    "total_revenue": 39630.00,
    "avg_tip_percentage": 19.45
  },
  "comparison": {
    "fare_difference": 0.76,
    "distance_difference": 0.45,
    "speed_difference": 2.31,
    "tip_difference": 1.56
  }
}
```

**Use Cases:**
- Identify weekend travel patterns
- Compare demand across week
- Revenue forecasting

**Example:**
```bash
curl http://127.0.0.1:5000/api/analysis/weekend-comparison
```

---

### Routes

#### `GET /api/routes/top`

Get most popular routes ranked by trip count using custom QuickSort algorithm.

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | int | 10 | Number of top routes to return |

**Response Structure:**
```json
[
  {
    "pickup_zone": "Times Square/Theatre District",
    "dropoff_zone": "Penn Station/Madison Sq West",
    "trip_count": 456,
    "avg_fare": 8.50,
    "avg_distance": 1.2,
    "total_revenue": 3876.00
  },
  {
    "pickup_zone": "Upper East Side South",
    "dropoff_zone": "Upper East Side North",
    "trip_count": 387,
    "avg_fare": 7.20,
    "avg_distance": 0.9,
    "total_revenue": 2786.40
  }
]
```

**Algorithm:** Uses custom QuickSort implementation (O(n log n) complexity)

**Examples:**

1. Get top 10 routes:
```bash
curl http://127.0.0.1:5000/api/routes/top
```

2. Get top 20 routes:
```bash
curl "http://127.0.0.1:5000/api/routes/top?limit=20"
```

**Use Cases:**
- Identify popular corridors
- Route optimization
- Demand forecasting

---

### Custom Insights

#### `GET /api/insights/custom`

Get advanced insights using custom algorithms (outlier detection, aggregation).

**Parameters:** None

**Response Structure:**
```json
{
  "outliers_detected": 127,
  "hourly_aggregation": [
    {
      "hour": 0,
      "total_trips": 245,
      "total_revenue": 2876.45,
      "total_distance": 514.5,
      "avg_fare": 11.74,
      "avg_distance": 2.10
    }
  ],
  "outlier_samples": [
    {
      "id": 1234,
      "fare_amount": 125.50,
      "trip_distance": 18.3,
      "duration_mins": 65.2,
      "reason": "fare_outlier",
      "outlier_type": "high"
    },
    {
      "id": 2456,
      "fare_amount": 2.50,
      "trip_distance": 0.1,
      "duration_mins": 1.2,
      "reason": "fare_outlier",
      "outlier_type": "low"
    }
  ]
}
```

**Algorithms Used:**
1. **IQR Outlier Detection** - Identifies anomalous fares using Interquartile Range method
2. **Manual Aggregation** - Hourly aggregation without pandas groupby
3. **QuickSort** - Custom sorting implementation

**Outlier Detection Method:**
- Calculate Q1 (25th percentile) and Q3 (75th percentile)
- Compute IQR = Q3 - Q1
- Flag values outside [Q1 - 1.5*IQR, Q3 + 1.5*IQR]

**Use Cases:**
- Data quality analysis
- Fraud detection
- Anomaly investigation

**Example:**
```bash
curl http://127.0.0.1:5000/api/insights/custom
```

---

## Data Models

### Trip Model

Complete structure of a trip record returned by the API:

```json
{
  "id": 1,
  "VendorID": 1,
  "tpep_pickup_datetime": "2019-01-01 00:46:40",
  "tpep_dropoff_datetime": "2019-01-01 00:53:20",
  "passenger_count": 1,
  "trip_distance": 1.5,
  "RatecodeID": 1,
  "store_and_fwd_flag": "N",
  "PULocationID": 142,
  "DOLocationID": 236,
  "payment_type": 1,
  "fare_amount": 7.0,
  "extra": 0.5,
  "mta_tax": 0.5,
  "tip_amount": 1.65,
  "tolls_amount": 0.0,
  "improvement_surcharge": 0.3,
  "total_amount": 11.15,
  "congestion_surcharge": 0.0,
  "pu_borough": "Manhattan",
  "pu_zone": "East Harlem North",
  "service_zone": "Boro Zone",
  "do_borough": "Manhattan",
  "do_zone": "Upper East Side North",
  "do_service_zone": "Yellow Zone",
  "duration_mins": 6.67,
  "avg_speed_mph": 13.5,
  "tip_percentage": 23.57,
  "pickup_hour": 0,
  "fare_range": "$5-$15",
  "distance_category": "short"
}
```

### Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `id` | int | Unique trip identifier |
| `VendorID` | int | Taxi company (1=Creative Mobile, 2=VeriFone) |
| `tpep_pickup_datetime` | datetime | Pickup timestamp |
| `tpep_dropoff_datetime` | datetime | Dropoff timestamp |
| `passenger_count` | int | Number of passengers |
| `trip_distance` | float | Distance in miles |
| `RatecodeID` | int | Rate code (1=Standard, 2=JFK, 3=Newark, etc.) |
| `store_and_fwd_flag` | string | Y/N (trip record held in memory) |
| `PULocationID` | int | Pickup location zone ID |
| `DOLocationID` | int | Dropoff location zone ID |
| `payment_type` | int | Payment method (1=Card, 2=Cash) |
| `fare_amount` | float | Metered fare ($) |
| `extra` | float | Extra charges ($) |
| `mta_tax` | float | MTA tax ($0.50) |
| `tip_amount` | float | Tip amount ($) |
| `tolls_amount` | float | Tolls paid ($) |
| `improvement_surcharge` | float | Improvement surcharge ($0.30) |
| `total_amount` | float | Total charge ($) |
| `congestion_surcharge` | float | Congestion fee ($) |
| `pu_borough` | string | Pickup borough name |
| `pu_zone` | string | Pickup zone name |
| `service_zone` | string | Service zone type |
| `do_borough` | string | Dropoff borough name |
| `do_zone` | string | Dropoff zone name |
| `do_service_zone` | string | Dropoff service zone |
| `duration_mins` | float | **Calculated:** Trip duration |
| `avg_speed_mph` | float | **Calculated:** Average speed |
| `tip_percentage` | float | **Calculated:** Tip as % of fare |
| `pickup_hour` | int | **Calculated:** Hour (0-23) |
| `fare_range` | string | **Calculated:** Fare bracket |
| `distance_category` | string | **Calculated:** Distance category |

---

## Filtering & Pagination

### Pagination

Use `limit` and `offset` for pagination:

```bash
# Page 1 (trips 0-49)
curl "http://127.0.0.1:5000/api/trips/list?limit=50&offset=0"

# Page 2 (trips 50-99)
curl "http://127.0.0.1:5000/api/trips/list?limit=50&offset=50"

# Page 3 (trips 100-149)
curl "http://127.0.0.1:5000/api/trips/list?limit=100&offset=100"
```

### Multiple Filters

Combine multiple filters in a single query:

```bash
curl "http://127.0.0.1:5000/api/trips/list?borough=Manhattan&min_fare=10&max_fare=20&hour=8&limit=100"
```

### Filter Combinations

**Example 1:** Manhattan trips during morning rush hour
```bash
curl "http://127.0.0.1:5000/api/trips/list?borough=Manhattan&hour=8&limit=50"
```

**Example 2:** High-value trips (fare > $50)
```bash
curl "http://127.0.0.1:5000/api/trips/list?min_fare=50&limit=25"
```

**Example 3:** Long-distance trips (> 10 miles)
```bash
curl "http://127.0.0.1:5000/api/trips/list?min_distance=10&limit=30"
```

**Example 4:** Weekend evening trips
```bash
curl "http://127.0.0.1:5000/api/trips/list?is_weekend=true&hour=20&limit=100"
```

**Example 5:** Date range filter
```bash
curl "http://127.0.0.1:5000/api/trips/list?start_date=2019-01-01&end_date=2019-01-07&limit=200"
```

---

## Examples

### Complete Use Case Examples

#### 1. Analyze Rush Hour Traffic

```bash
# Get hourly patterns
curl http://127.0.0.1:5000/api/analysis/hourly-patterns > hourly_data.json

# Get speed analysis
curl http://127.0.0.1:5000/api/analysis/speed > speed_data.json

# Get trips during peak hours (8 AM)
curl "http://127.0.0.1:5000/api/trips/list?hour=8&limit=100" > morning_rush.json
```

#### 2. Borough Comparison Study

```bash
# Get borough statistics
curl http://127.0.0.1:5000/api/analysis/borough > borough_stats.json

# Get Manhattan trips
curl "http://127.0.0.1:5000/api/trips/list?borough=Manhattan&limit=100" > manhattan.json

# Get Brooklyn trips
curl "http://127.0.0.1:5000/api/trips/list?borough=Brooklyn&limit=100" > brooklyn.json
```

#### 3. Revenue Analysis

```bash
# Get summary statistics
curl http://127.0.0.1:5000/api/stats/summary > summary.json

# Get fare distribution
curl http://127.0.0.1:5000/api/analysis/fare-distribution > fare_dist.json

# Get high-value trips
curl "http://127.0.0.1:5000/api/trips/list?min_fare=50&limit=50" > high_value.json
```

#### 4. Route Optimization

```bash
# Get top 20 popular routes
curl "http://127.0.0.1:5000/api/routes/top?limit=20" > popular_routes.json

# Get distance analysis
curl http://127.0.0.1:5000/api/analysis/distance > distance_patterns.json
```

#### 5. Tipping Behavior Study

```bash
# Get tip analysis
curl http://127.0.0.1:5000/api/analysis/tips > tipping_data.json

# Get payment analysis
curl http://127.0.0.1:5000/api/analysis/payment > payment_methods.json

# Get credit card trips (payment_type=1)
curl "http://127.0.0.1:5000/api/trips/list?limit=100" > trips_sample.json
```

#### 6. Weekend vs Weekday Analysis

```bash
# Get weekend comparison
curl http://127.0.0.1:5000/api/analysis/weekend-comparison > weekend_vs_weekday.json

# Get weekend trips
curl "http://127.0.0.1:5000/api/trips/list?is_weekend=true&limit=100" > weekend_trips.json

# Get weekday trips
curl "http://127.0.0.1:5000/api/trips/list?is_weekend=false&limit=100" > weekday_trips.json
```

### Python Example

```python
import requests

BASE_URL = "http://127.0.0.1:5000"

# Get summary statistics
response = requests.get(f"{BASE_URL}/api/stats/summary")
summary = response.json()
print(f"Total trips: {summary['total_trips']}")
print(f"Average fare: ${summary['avg_fare']:.2f}")

# Get Manhattan trips with filters
params = {
    'borough': 'Manhattan',
    'min_fare': 10,
    'max_fare': 20,
    'limit': 50
}
response = requests.get(f"{BASE_URL}/api/trips/list", params=params)
trips = response.json()['trips']
print(f"Found {len(trips)} trips")

# Get hourly patterns
response = requests.get(f"{BASE_URL}/api/analysis/hourly-patterns")
hourly_data = response.json()
for hour_data in hourly_data:
    print(f"Hour {hour_data['hour']}: {hour_data['trip_count']} trips")
```

### JavaScript Example

```javascript
const BASE_URL = 'http://127.0.0.1:5000';

// Get summary statistics
fetch(`${BASE_URL}/api/stats/summary`)
  .then(response => response.json())
  .then(data => {
    console.log('Total trips:', data.total_trips);
    console.log('Average fare:', data.avg_fare);
  });

// Get trips with filters
const params = new URLSearchParams({
  borough: 'Manhattan',
  min_fare: 10,
  max_fare: 20,
  limit: 50
});

fetch(`${BASE_URL}/api/trips/list?${params}`)
  .then(response => response.json())
  .then(data => {
    console.log('Trips found:', data.trips.length);
    data.trips.forEach(trip => {
      console.log(`Trip ${trip.id}: $${trip.fare_amount}`);
    });
  });

// Get top routes
fetch(`${BASE_URL}/api/routes/top?limit=10`)
  .then(response => response.json())
  .then(routes => {
    routes.forEach((route, index) => {
      console.log(`${index + 1}. ${route.pickup_zone} → ${route.dropoff_zone}`);
      console.log(`   ${route.trip_count} trips, $${route.avg_fare} avg fare`);
    });
  });
```

---

## Database Schema Reference

### trips Table (30 columns, 6 indexes, 2 FKs)

```sql
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
    
    INDEX idx_pickup_location (PULocationID),
    INDEX idx_dropoff_location (DOLocationID),
    INDEX idx_pickup_datetime (tpep_pickup_datetime),
    INDEX idx_pickup_hour (pickup_hour),
    INDEX idx_pu_borough (pu_borough),
    INDEX idx_do_borough (do_borough),
    
    FOREIGN KEY (PULocationID) REFERENCES zones(LocationID) ON DELETE SET NULL,
    FOREIGN KEY (DOLocationID) REFERENCES zones(LocationID) ON DELETE SET NULL
);
```

### excluded_data_log Table (7 columns, 2 indexes)

```sql
CREATE TABLE excluded_data_log (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    issue_type VARCHAR(50) NOT NULL,
    trip_identifier VARCHAR(255),
    field_name VARCHAR(50),
    issue_description TEXT,
    action_taken VARCHAR(100),
    logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_issue_type (issue_type),
    INDEX idx_logged_at (logged_at)
);
```

**Purpose:** Tracks data quality issues and rejected records during ETL processing.

**Use Cases:**
- Data quality monitoring
- ETL audit trail
- Debugging data issues
- Compliance and lineage tracking

### zones Table (4 columns, 2 indexes)

```sql
CREATE TABLE zones (
    LocationID INT PRIMARY KEY,
    Borough VARCHAR(50),
    Zone VARCHAR(100),
    service_zone VARCHAR(50),
    
    INDEX idx_borough (Borough),
    INDEX idx_zone (Zone)
);
```

### taxi_zones Table (6 columns, 3 indexes, 1 FK)

```sql
CREATE TABLE taxi_zones (
    objectid INT PRIMARY KEY,
    shape_leng DECIMAL(15, 10),
    shape_area DECIMAL(15, 10),
    zone VARCHAR(100),
    locationid INT,
    borough VARCHAR(50),
    
    INDEX idx_locationid (locationid),
    INDEX idx_borough (borough),
    INDEX idx_zone (zone),
    
    FOREIGN KEY (locationid) REFERENCES zones(LocationID) ON DELETE CASCADE
);
```

---

## Performance Tips

1. **Use Pagination:** Always use `limit` and `offset` for large datasets
2. **Filter Early:** Apply filters to reduce data transfer
3. **Index Usage:** Database has indexes on borough, hour, datetime columns
4. **Caching:** Consider caching frequently accessed endpoints (summary, hourly patterns)
5. **Batch Requests:** Combine multiple filters in one request instead of multiple calls

---

## Rate Limiting

**Current Status:** No rate limiting implemented

**Recommendation:** For production, implement rate limiting to prevent abuse.

---

## CORS Configuration

**Allowed Origins:**
- `http://127.0.0.1:5500`
- `http://localhost:5500`

To add more origins, edit the CORS configuration in `app.py`:

```python
CORS(
    app,
    supports_credentials=True,
    origins=[
        'http://127.0.0.1:5500',
        'http://localhost:5500',
     ]
)
```

---

## Troubleshooting

### Common Issues

**Problem:** API returns empty results
- **Solution:** Check if database has data. Run ETL pipeline: `python main.py`

**Problem:** CORS error in browser
- **Solution:** Add your frontend URL to CORS origins in `app.py`

**Problem:** 500 Internal Server Error
- **Solution:** Check MySQL connection in `.env` file and verify database exists

**Problem:** Slow response times
- **Solution:** Add database indexes, reduce `limit` parameter, or use more specific filters

---
