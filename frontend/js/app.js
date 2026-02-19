// app.js - Main Application Logic and Tab Switching
// Handles UI state, tab navigation, and data orchestration

// ========================================
// GLOBAL STATE
// ========================================

let currentTrips = [];
let currentPage = 1;
const pageSize = 20;
let activeTab = 'overview';
let isLoadingOverview = false;
let isLoadingAnalytics = false;
let isLoadingReports = false;
let chartsInitialized = {
    overview: false,
    analytics: false
};

// ========================================
// INITIALIZATION
// ========================================

/**
 * Initialize the application
 */
function init() {
    setupTabNavigation();
    checkAPIConnection();
    initFilters(onFiltersChanged);
    
    // Load overview data once on init
    setTimeout(() => loadOverviewData(), 100);
    
    // Debounced resize handler
    let resizeTimeout;
    window.addEventListener('resize', () => {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(() => {
            if (activeTab === 'overview' && chartsInitialized.overview) {
                refreshOverviewCharts();
            } else if (activeTab === 'analytics' && chartsInitialized.analytics) {
                refreshAnalyticsCharts();
            }
        }, 250);
    });
}

/**
 * Check API status and update badge
 */
function checkAPIConnection() {
    fetch('http://127.0.0.1:5000/api/status')
        .then(res => res.json())
        .then(status => {
            updateAPIStatusBadge('Live', true);
        })
        .catch(error => {
            updateAPIStatusBadge('Offline', false);
            console.error('API connection failed:', error);
        });
}

/**
 * Update API status badge in header
 */
function updateAPIStatusBadge(text, isOnline) {
    const badge = document.getElementById('api-status');
    if (badge) {
        badge.textContent = text;
        badge.className = isOnline ? 'badge badge-live' : 'badge badge-offline';
    }
}

// ========================================
// TAB NAVIGATION
// ========================================

/**
 * Setup tab navigation event listeners
 */
function setupTabNavigation() {
    const tabButtons = document.querySelectorAll('.tab-button');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const tabName = button.getAttribute('data-tab');
            switchTab(tabName);
        });
    });
}

/**
 * Switch between tabs
 * @param {string} tabName - Name of tab to switch to
 */
function switchTab(tabName) {
    activeTab = tabName;
    
    // Update tab buttons
    document.querySelectorAll('.tab-button').forEach(btn => {
        btn.classList.remove('active');
        if (btn.getAttribute('data-tab') === tabName) {
            btn.classList.add('active');
        }
    });
    
    // Update tab content
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    
    const activeContent = document.getElementById(`tab-${tabName}`);
    if (activeContent) {
        activeContent.classList.add('active');
    }
    
    // Load data for the active tab
    switch(tabName) {
        case 'overview':
            loadOverviewData();
            break;
        case 'analytics':
            loadAnalyticsData();
            break;
        case 'reports':
            loadReportsData();
            break;
    }
}

// ========================================
// OVERVIEW TAB
// ========================================

/**
 * Load data for Overview tab
 */
function loadOverviewData() {
    if (isLoadingOverview || chartsInitialized.overview) return;
    isLoadingOverview = true;
    
    fetchSummaryStats()
        .then(stats => {
            updateOverviewSummaryCards(stats);
        })
        .catch(error => {
            console.error('Failed to load summary stats:', error);
            // Set default values on error
            updateOverviewSummaryCards({
                total_trips: 0,
                avg_fare: 0,
                avg_distance: 0,
                avg_duration: 0
            });
        });
    
    // Load data for charts only if not already initialized
    Promise.all([
        fetchHourlyPatterns().catch(e => []),
        fetchBoroughAnalysis().catch(e => []),
        fetchDistanceAnalysis().catch(e => [])
    ])
    .then(([hourly, borough, distance]) => {
        renderOverviewCharts(hourly, borough, distance);
        chartsInitialized.overview = true;
    })
    .catch(error => {
        console.error('Failed to load overview charts:', error);
    })
    .finally(() => {
        isLoadingOverview = false;
    });
}

/**
 * Update summary cards in Overview tab
 */
function updateOverviewSummaryCards(stats) {
    if (stats.total_trips !== undefined) {
        setText('card-total-trips', formatNumber(stats.total_trips));
    }
    if (stats.avg_fare !== undefined) {
        setText('card-avg-fare', '$' + parseFloat(stats.avg_fare).toFixed(2));
    }
    if (stats.avg_distance !== undefined) {
        setText('card-avg-distance', parseFloat(stats.avg_distance).toFixed(1) + ' mi');
    }
    if (stats.avg_duration !== undefined) {
        setText('card-avg-duration', Math.round(stats.avg_duration) + ' min');
    }
}

/**
 * Render charts for Overview tab
 */
function renderOverviewCharts(hourlyData, boroughData, distanceData) {
    if (hourlyData) {
        createHourlyChart(hourlyData);
    }
    if (boroughData) {
        createBoroughChart(boroughData);
    }
    if (distanceData) {
        createDistanceChart(distanceData);
    }
}

/**
 * Refresh overview charts (on resize)
 */
function refreshOverviewCharts() {
    try {
        if (window.hourlyChart && typeof window.hourlyChart.resize === 'function') {
            window.hourlyChart.resize();
        }
        if (window.boroughChart && typeof window.boroughChart.resize === 'function') {
            window.boroughChart.resize();
        }
        if (window.distanceChart && typeof window.distanceChart.resize === 'function') {
            window.distanceChart.resize();
        }
    } catch (error) {
        console.error('Error refreshing charts:', error);
    }
}

// ========================================
// ANALYTICS TAB
// ========================================

/**
 * Load data for Analytics tab
 */
function loadAnalyticsData() {
    if (isLoadingAnalytics || chartsInitialized.analytics) return;
    isLoadingAnalytics = true;
    
    Promise.all([
        fetchPaymentAnalysis().catch(e => []),
        fetchSpeedAnalysis().catch(e => []),
        fetchWeekendComparison().catch(e => []),
        fetchTipAnalysis().catch(e => []),
        fetchTopRoutes(10).catch(e => [])
    ])
    .then(([payment, speed, weekend, tips, routes]) => {
        renderAnalyticsCharts(payment, speed, weekend, tips, routes);
        chartsInitialized.analytics = true;
    })
    .catch(error => {
        console.error('Failed to load analytics data:', error);
    })
    .finally(() => {
        isLoadingAnalytics = false;
    });
}

/**
 * Render charts for Analytics tab
 */
function renderAnalyticsCharts(paymentData, speedData, weekendData, tipsData, routesData) {
    if (paymentData) {
        createPaymentChart(paymentData);
    }
    if (speedData) {
        createSpeedChart(speedData);
    }
    if (weekendData) {
        createWeekendChart(weekendData);
    }
    if (tipsData) {
        createTipsChart(tipsData);
    }
    if (routesData) {
        createRoutesChart(routesData);
    }
}

/**
 * Refresh analytics charts (on resize)
 */
function refreshAnalyticsCharts() {
    try {
        if (window.paymentChart && typeof window.paymentChart.resize === 'function') {
            window.paymentChart.resize();
        }
        if (window.speedChart && typeof window.speedChart.resize === 'function') {
            window.speedChart.resize();
        }
        if (window.weekendChart && typeof window.weekendChart.resize === 'function') {
            window.weekendChart.resize();
        }
        if (window.tipsChart && typeof window.tipsChart.resize === 'function') {
            window.tipsChart.resize();
        }
        if (window.routesChart && typeof window.routesChart.resize === 'function') {
            window.routesChart.resize();
        }
    } catch (error) {
        console.error('Error refreshing charts:', error);
    }
}

// ========================================
// REPORTS TAB
// ========================================

/**
 * Load data for Reports tab
 */
function loadReportsData() {
    if (isLoadingReports) return;
    isLoadingReports = true;
    
    onFiltersChanged();
    
    setTimeout(() => {
        isLoadingReports = false;
    }, 500);
}

/**
 * Handle filter changes
 */
function onFiltersChanged() {
    const filters = getFilterValues();
    
    fetchTrips(filters)
        .then(trips => {
            trips = applyLocalFilters(trips, filters);
            
            const sortField = getSortField();
            const sortOrder = getSortOrder();
            trips = sortTrips(trips, sortField, sortOrder);
            
            currentTrips = trips;
            currentPage = 1;
            
            renderTable(trips);
            updateResultCount(trips.length);
        })
        .catch(error => {
            console.error('Failed to load trips:', error);
            const resultCount = document.getElementById('result-count');
            if (resultCount) {
                resultCount.textContent = 'Error loading data';
            }
        });
}

/**
 * Apply local filters to trip data
 */
function applyLocalFilters(trips, filters) {
    return trips.filter(trip => {
        // Handle invalid pickupTime
        const pickupTime = trip.pickupTime;
        if (!pickupTime || !(pickupTime instanceof Date) || isNaN(pickupTime.getTime())) {
            return true; // Keep trips with invalid dates but don't filter by hour
        }
        
        const hour = pickupTime.getHours();
        
        if (hour < filters.minHour || hour > filters.maxHour) return false;
        if (trip.distance < filters.minDistance || trip.distance > filters.maxDistance) return false;
        if (trip.fareAmount < filters.minFare || trip.fareAmount > filters.maxFare) return false;
        
        return true;
    });
}

/**
 * Render trips table
 */
function renderTable(trips) {
    const tbody = document.getElementById('trips-tbody');
    if (!tbody) return;
    
    const start = (currentPage - 1) * pageSize;
    const end = Math.min(start + pageSize, trips.length);
    const pageTrips = trips.slice(start, end);
    
    const rows = pageTrips.map(trip => `
        <tr>
            <td>${formatDateTime(trip.pickupTime)}</td>
            <td>${escapeHtml(trip.pickupZone)}</td>
            <td>${escapeHtml(trip.dropoffZone)}</td>
            <td>${escapeHtml(trip.pickupBorough)}</td>
            <td>${trip.distance.toFixed(1)} mi</td>
            <td>${Math.round(trip.duration)} min</td>
            <td>$${trip.fareAmount.toFixed(2)}</td>
            <td>$${trip.totalAmount.toFixed(2)}</td>
        </tr>
    `);
    
    tbody.innerHTML = rows.join('');
    renderPagination(trips.length);
}

/**
 * Render pagination controls
 */
function renderPagination(total) {
    const container = document.getElementById('pagination');
    if (!container) return;
    
    const totalPages = Math.ceil(total / pageSize);
    if (totalPages <= 1) {
        container.innerHTML = '';
        return;
    }
    
    const buttons = [];
    buttons.push(`<button class="page-btn" ${currentPage === 1 ? 'disabled' : ''} onclick="goToPage(${currentPage - 1})">« Prev</button>`);
    
    for (let p = 1; p <= totalPages; p++) {
        if (p === currentPage) {
            buttons.push(`<button class="page-btn active">${p}</button>`);
        } else {
            buttons.push(`<button class="page-btn" onclick="goToPage(${p})">${p}</button>`);
        }
    }
    
    buttons.push(`<button class="page-btn" ${currentPage === totalPages ? 'disabled' : ''} onclick="goToPage(${currentPage + 1})">Next »</button>`);
    container.innerHTML = buttons.join('');
}

/**
 * Go to specific page
 */
function goToPage(page) {
    currentPage = page;
    renderTable(currentTrips);
    
    const tableSection = document.getElementById('trips-table-section');
    if (tableSection) {
        tableSection.scrollIntoView({ behavior: 'smooth' });
    }
}

/**
 * Update result count display
 */
function updateResultCount(count) {
    setText('result-count', `${formatNumber(count)} trips`);
}

// ========================================
// UTILITY FUNCTIONS
// ========================================

/**
 * Set text content of element
 */
function setText(id, text) {
    const element = document.getElementById(id);
    if (element) {
        element.textContent = text;
    }
}

/**
 * Format number with thousands separator
 */
function formatNumber(num) {
    return num.toLocaleString();
}

/**
 * Format hour as 12-hour time
 */
function formatHour(hour) {
    if (hour === 0) return '12:00 AM';
    if (hour < 12) return `${hour}:00 AM`;
    if (hour === 12) return '12:00 PM';
    return `${hour - 12}:00 PM`;
}

/**
 * Format date and time
 */
function formatDateTime(date) {
    // Handle invalid dates
    if (!date || !(date instanceof Date) || isNaN(date.getTime())) {
        return 'N/A';
    }
    const month = date.getMonth() + 1;
    const day = date.getDate();
    const hours = date.getHours();
    const minutes = date.getMinutes();
    const ampm = hours >= 12 ? 'PM' : 'AM';
    const displayHour = hours % 12 || 12;
    const minStr = minutes < 10 ? '0' + minutes : '' + minutes;
    return `${month}/${day} ${displayHour}:${minStr} ${ampm}`;
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ========================================
// START APPLICATION
// ========================================

document.addEventListener('DOMContentLoaded', init);
