// api.js - talks to the Flask backend

var API_BASE = 'http://localhost:5001/api';

function fetchTrips(filters) {
    var url = API_BASE + '/trips?limit=500';

    if (filters.borough && filters.borough !== 'All') {
        url += '&borough=' + encodeURIComponent(filters.borough);
    }

    return fetch(url)
        .then(function (res) {
            return res.json();
        })
        .then(function (data) {
            var trips = [];
            for (var i = 0; i < data.length; i++) {
                trips.push(mapTrip(data[i]));
            }
            return trips;
        });
}

function mapTrip(t) {
    return {
        pickupTime: new Date(t.pickup_datetime),
        dropoffTime: new Date(t.dropoff_datetime),
        pickupZone: t.pickup_zone || 'Unknown',
        dropoffZone: t.dropoff_zone || 'Unknown',
        pickupBorough: t.pickup_borough || 'Unknown',
        dropoffBorough: t.dropoff_borough || 'Unknown',
        distance: t.trip_distance || 0,
        duration: t.trip_duration_minutes || 0,
        fareAmount: t.fare_amount || 0,
        totalAmount: t.total_amount || 0,
        farePerMile: t.fare_per_mile || 0,
        pickupHourRaw: t.pickup_hour || 0
    };
}

function fetchStats() {
    return fetch(API_BASE + '/stats')
        .then(function (res) {
            return res.json();
        });
}
