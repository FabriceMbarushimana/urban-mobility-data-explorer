-- zones table (4 columns)
-- Reference table for NYC taxi zones with borough mapping
CREATE TABLE zones (
    LocationID INT PRIMARY KEY,
    Borough VARCHAR(50),
    Zone VARCHAR(100),
    service_zone VARCHAR(50),
    
    INDEX idx_borough (Borough),
    INDEX idx_zone (Zone)
);

-- taxi_zones table (geographic zone data)
-- Stores detailed geographic information for each taxi zone
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

-- trips table (30 columns)
-- Main table storing NYC taxi trip records with enriched features
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
