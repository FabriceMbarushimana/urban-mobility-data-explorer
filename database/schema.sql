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
