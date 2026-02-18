CREATE DATABASE IF NOT EXISTS urban_mobility;
USE urban_mobility;

DROP TABLE IF EXISTS trips;
DROP TABLE IF EXISTS zones;

CREATE TABLE zones (
    zone_id INT PRIMARY KEY,
    borough VARCHAR(50) NOT NULL,
    zone_name VARCHAR(100) NOT NULL,
    service_zone VARCHAR(100),
    geometry JSON
) ENGINE=InnoDB;

CREATE TABLE trips (
    trip_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    pickup_datetime DATETIME NOT NULL,
    dropoff_datetime DATETIME NOT NULL,
    pickup_zone_id INT NOT NULL,
    dropoff_zone_id INT NOT NULL,
    trip_distance DECIMAL(6,2),
    fare_amount DECIMAL(8,2),
    total_amount DECIMAL(8,2),
    trip_duration_minutes DECIMAL(6,2),
    fare_per_mile DECIMAL(6,2),
    pickup_hour INT,
   CONSTRAINT fk_pickup_zone FOREIGN KEY (pickup_zone_id) REFERENCES zones(zone_id),
    CONSTRAINT fk_dropoff_zone FOREIGN KEY (dropoff_zone_id) REFERENCES zones(zone_id)
) ENGINE=InnoDB;
