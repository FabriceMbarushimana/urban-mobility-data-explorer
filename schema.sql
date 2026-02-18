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

