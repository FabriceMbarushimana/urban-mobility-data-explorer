USE urban_mobility;

CREATE INDEX idx_pickup_datetime ON trips(pickup_datetime);
CREATE INDEX idx_dropoff_datetime ON trips(dropoff_datetime);
CREATE INDEX idx_pickup_zone ON trips(pickup_zone_id);
CREATE INDEX idx_dropoff_zone ON trips(dropoff_zone_id);
CREATE INDEX idx_fare_amount ON trips(fare_amount);
CREATE INDEX idx_total_amount ON trips(total_amount);
CREATE INDEX idx_trip_distance ON trips(trip_distance);
CREATE INDEX idx_trip_duration_minutes ON trips(trip_duration_minutes);
CREATE INDEX idx_fare_per_mile ON trips(fare_per_mile);
CREATE INDEX idx_pickup_hour ON trips(pickup_hour);

CREATE UNIQUE INDEX idx_zone_id ON zones(zone_id);
CREATE INDEX idx_borough ON zones(borough);
CREATE INDEX idx_zone_name ON zones(zone_name);
