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
