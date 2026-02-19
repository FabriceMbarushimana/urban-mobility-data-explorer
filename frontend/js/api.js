// api.js - Flask Backend API Integration
// All API endpoints for NYC Urban Mobility Explorer

const API_BASE = 'http://127.0.0.1:5000/api';

// ========================================
// UTILITY FUNCTIONS
// ========================================

/**
 * Generic fetch wrapper with error handling
 * @param {string} url - API endpoint URL
 * @param {object} options - Fetch options
 * @returns {Promise} - JSON response or error
 */
function apiFetch(url, options = {}) {
    return fetch(url, {
        ...options,
        credentials: 'include',
        headers: {
            'Content-Type': 'application/json',
            ...options.headers
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        return response.json();
    })
    .catch(error => {
        console.error('API Error:', error);
        throw error;
    });
}

/**
 * Build query string from parameters object
 * @param {object} params - Query parameters
 * @returns {string} - Query string
 */
function buildQueryString(params) {
    const query = Object.keys(params)
        .filter(key => params[key] !== null && params[key] !== undefined && params[key] !== '')
        .map(key => `${encodeURIComponent(key)}=${encodeURIComponent(params[key])}`)
        .join('&');
    return query ? `?${query}` : '';
}

// ========================================
// STATUS & HEALTH CHECK
// ========================================

/**
 * Check API status
 * @returns {Promise} - API status object
 */
function checkAPIStatus() {
    return apiFetch(`${API_BASE}/status`);
}

// ========================================
// STATISTICS ENDPOINTS
// ========================================

/**
 * Get overall dataset summary statistics
 * @returns {Promise} - Summary statistics object
 */
function fetchSummaryStats() {
    return apiFetch(`${API_BASE}/stats/summary`);
}

// ========================================
// TRIPS DATA ENDPOINTS
// ========================================

/**
 * Get trips with optional filtering and pagination
 * @param {object} filters - Filter parameters
 * @returns {Promise} - List of trip records
 */
function fetchTrips(filters = {}) {
    const params = {
        limit: filters.limit || 100,
        offset: filters.offset || 0,
        borough: filters.borough && filters.borough !== 'All' ? filters.borough : null,
        min_fare: filters.minFare,
        max_fare: filters.maxFare,
        min_distance: filters.minDistance,
        max_distance: filters.maxDistance,
        start_date: filters.startDate,
        end_date: filters.endDate,
        hour: filters.hour,
        is_weekend: filters.isWeekend
    };
    
    const queryString = buildQueryString(params);
    return apiFetch(`${API_BASE}/trips/list${queryString}`)
        .then(data => {
            if (data.trips && Array.isArray(data.trips)) {
                return data.trips.map(mapTripData);
            }
            return [];
        });
}

/**
 * Map trip data from API response to frontend format
 * @param {object} trip - Raw trip data from API
 * @returns {object} - Formatted trip object
 */
function mapTripData(trip) {
    return {
        pickupTime: new Date(trip.tpep_pickup_datetime),
        dropoffTime: new Date(trip.tpep_dropoff_datetime),
        pickupZone: trip.pu_zone || 'Unknown',
        dropoffZone: trip.do_zone || 'Unknown',
        pickupBorough: trip.pu_borough || 'Unknown',
        dropoffBorough: trip.do_borough || 'Unknown',
        distance: parseFloat(trip.trip_distance) || 0,
        duration: parseFloat(trip.duration_mins) || 0,
        fareAmount: parseFloat(trip.fare_amount) || 0,
        totalAmount: parseFloat(trip.total_amount) || 0,
        farePerMile: parseFloat(trip.fare_per_mile) || 0,
        pickupHour: trip.pickup_hour || 0,
        paymentType: trip.payment_type || 'Unknown',
        tipAmount: parseFloat(trip.tip_amount) || 0
    };
}

// ========================================
// ANALYSIS ENDPOINTS
// ========================================

/**
 * Get trip patterns aggregated by hour of day
 * @returns {Promise} - Hourly pattern statistics
 */
function fetchHourlyPatterns() {
    return apiFetch(`${API_BASE}/analysis/hourly-patterns`);
}

/**
 * Get analysis grouped by NYC borough
 * @returns {Promise} - Borough-level statistics
 */
function fetchBoroughAnalysis() {
    return apiFetch(`${API_BASE}/analysis/borough`);
}

/**
 * Get fare amount distribution
 * @returns {Promise} - Fare distribution data
 */
function fetchFareDistribution() {
    return apiFetch(`${API_BASE}/analysis/fare-distribution`);
}

/**
 * Get distance-based insights and patterns
 * @returns {Promise} - Distance analysis data
 */
function fetchDistanceAnalysis() {
    return apiFetch(`${API_BASE}/analysis/distance`);
}

/**
 * Get payment type distribution
 * @returns {Promise} - Payment analysis data
 */
function fetchPaymentAnalysis() {
    return apiFetch(`${API_BASE}/analysis/payment`);
}

/**
 * Get average speed analysis by hour of day
 * @returns {Promise} - Speed analysis data
 */
function fetchSpeedAnalysis() {
    return apiFetch(`${API_BASE}/analysis/speed`);
}

/**
 * Get tip percentage analysis and patterns
 * @returns {Promise} - Tip analysis data
 */
function fetchTipAnalysis() {
    return apiFetch(`${API_BASE}/analysis/tips`);
}

/**
 * Get weekend vs weekday comparison
 * @returns {Promise} - Weekend comparison data
 */
function fetchWeekendComparison() {
    return apiFetch(`${API_BASE}/analysis/weekend-comparison`);
}

// ========================================
// ROUTES ENDPOINTS
// ========================================

/**
 * Get most popular routes
 * @param {number} limit - Number of top routes to return
 * @returns {Promise} - Top routes data
 */
function fetchTopRoutes(limit = 10) {
    const queryString = buildQueryString({ limit });
    return apiFetch(`${API_BASE}/routes/top${queryString}`);
}

// ========================================
// CUSTOM INSIGHTS ENDPOINTS
// ========================================

/**
 * Get insights using custom algorithms
 * @returns {Promise} - Custom insights data
 */
function fetchCustomInsights() {
    return apiFetch(`${API_BASE}/insights/custom`);
}
