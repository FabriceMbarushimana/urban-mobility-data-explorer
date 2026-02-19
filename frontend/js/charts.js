// charts.js - Chart Rendering with Chart.js
// All chart creation and management functions

// ========================================
// CHART CONFIGURATION
// ========================================

const chartColors = {
    primary: '#2d5f2d',
    secondary: '#c4553a',
    accent: '#4a7c59',
    highlight: '#d97654',
    neutral: '#6b6b6b',
    lightGray: '#e0ddd4',
    background: '#faf9f7'
};

// Track if charts are currently rendering
const chartRenderStates = {
    hourly: false,
    borough: false,
    distance: false,
    payment: false,
    speed: false,
    weekend: false,
    tips: false,
    routes: false
};

const defaultChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    animation: {
        duration: 750,
        easing: 'easeInOutQuart'
    },
    plugins: {
        legend: {
            display: true,
            position: 'top'
        }
    }
};

// ========================================
// OVERVIEW TAB CHARTS
// ========================================

/**
 * Create hourly trip volume chart
 * @param {object} data - Hourly patterns data from API
 */
function createHourlyChart(data) {
    if (chartRenderStates.hourly) return;
    chartRenderStates.hourly = true;
    
    const ctx = document.getElementById('chart-hourly');
    if (!ctx) {
        chartRenderStates.hourly = false;
        return;
    }
    
    // Destroy existing chart if present
    if (window.hourlyChart && typeof window.hourlyChart.destroy === 'function') {
        window.hourlyChart.destroy();
        window.hourlyChart = null;
    }
    
    // Normalize data - API returns array of {pickup_hour, trip_count, avg_fare, ...}
    const hourlyData = Array.isArray(data) ? data : [];
    if (hourlyData.length === 0) {
        console.warn('No hourly data available');
        chartRenderStates.hourly = false;
        return;
    }
    
    // Extract hours and counts from normalized data
    const hours = hourlyData.map(d => d.pickup_hour ?? d.hour ?? 0);
    const counts = hourlyData.map(d => d.trip_count ?? d.total_trips ?? 0);
    
    // Color bars based on peak hours
    const backgroundColors = hours.map(hour => {
        return (hour >= 7 && hour <= 9) || (hour >= 17 && hour <= 19) 
            ? chartColors.secondary 
            : chartColors.primary;
    });
    
    try {
        window.hourlyChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: hours.map(h => {
                    if (h === 0) return '12AM';
                    if (h < 12) return `${h}AM`;
                    if (h === 12) return '12PM';
                    return `${h-12}PM`;
                }),
                datasets: [{
                    label: 'Trips',
                    data: counts,
                    backgroundColor: backgroundColors,
                    borderColor: backgroundColors,
                    borderWidth: 1
                }]
            },
            options: {
                ...defaultChartOptions,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `Trips: ${context.parsed.y.toLocaleString()}`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return value.toLocaleString();
                            }
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error creating hourly chart:', error);
    } finally {
        chartRenderStates.hourly = false;
    }
}

/**
 * Create borough average fare chart
 * @param {object} data - Borough analysis data from API
 */
function createBoroughChart(data) {
    if (chartRenderStates.borough) return;
    chartRenderStates.borough = true;
    
    const ctx = document.getElementById('chart-borough');
    if (!ctx) {
        chartRenderStates.borough = false;
        return;
    }
    
    if (window.boroughChart && typeof window.boroughChart.destroy === 'function') {
        window.boroughChart.destroy();
        window.boroughChart = null;
    }
    
    // Normalize data - API returns array of {Borough, total_trips, avg_fare, ...}
    const boroughData = Array.isArray(data) ? data : [];
    if (boroughData.length === 0) {
        console.warn('No borough data available');
        chartRenderStates.borough = false;
        return;
    }
    
    // Extract labels and fares - handle different field names
    const labels = boroughData.map(b => b.Borough ?? b.borough ?? b.pu_borough ?? 'Unknown');
    const avgFares = boroughData.map(b => parseFloat(b.avg_fare ?? b.average_fare ?? 0));
    
    try {
        window.boroughChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Average Fare ($)',
                data: avgFares,
                backgroundColor: chartColors.accent,
                borderColor: chartColors.primary,
                borderWidth: 1
            }]
        },
        options: {
            ...defaultChartOptions,
            indexAxis: 'y',
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `$${context.parsed.x.toFixed(2)}`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return '$' + value;
                        }
                    }
                }
            }
        }
    });
    } catch (error) {
        console.error('Error creating borough chart:', error);
    } finally {
        chartRenderStates.borough = false;
    }
}

/**
 * Create distance distribution chart
 * @param {object} data - Distance analysis data from API
 */
function createDistanceChart(data) {
    if (chartRenderStates.distance) return;
    chartRenderStates.distance = true;
    
    const ctx = document.getElementById('chart-distance');
    if (!ctx) {
        chartRenderStates.distance = false;
        return;
    }
    
    if (window.distanceChart && typeof window.distanceChart.destroy === 'function') {
        window.distanceChart.destroy();
        window.distanceChart = null;
    }
    
    // Normalize data - API returns array of {distance_category, trip_count, avg_fare, ...}
    const distanceData = Array.isArray(data) ? data : [];
    if (distanceData.length === 0) {
        console.warn('No distance data available');
        chartRenderStates.distance = false;
        return;
    }
    
    // Extract labels and counts - handle different field names
    const labels = distanceData.map(d => d.distance_category ?? d.range ?? 'Unknown');
    const counts = distanceData.map(d => d.trip_count ?? d.count ?? 0);
    
    try {
        window.distanceChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Trip Count',
                data: counts,
                backgroundColor: chartColors.primary,
                borderColor: chartColors.accent,
                borderWidth: 1
            }]
        },
        options: {
            ...defaultChartOptions,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `Trips: ${context.parsed.y.toLocaleString()}`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return value.toLocaleString();
                        }
                    }
                }
            }
        }
    });
    } catch (error) {
        console.error('Error creating distance chart:', error);    } finally {
        chartRenderStates.distance = false;    }
}

// ========================================
// ANALYTICS TAB CHARTS
// ========================================

/**
 * Create payment method distribution chart
 * @param {object} data - Payment analysis data from API
 */
function createPaymentChart(data) {
    if (chartRenderStates.payment) return;
    chartRenderStates.payment = true;
    
    const ctx = document.getElementById('chart-payment');
    if (!ctx) {
        chartRenderStates.payment = false;
        return;
    }
    
    if (window.paymentChart && typeof window.paymentChart.destroy === 'function') {
        window.paymentChart.destroy();
        window.paymentChart = null;
    }
    
    // Normalize data - API returns array of {payment_type, trip_count, avg_fare, ...}
    const paymentData = Array.isArray(data) ? data : [];
    if (paymentData.length === 0) {
        console.warn('No payment data available');
        chartRenderStates.payment = false;
        return;
    }
    
    // Map payment type codes to labels
    const paymentLabels = { 1: 'Credit Card', 2: 'Cash', 3: 'No Charge', 4: 'Dispute', 5: 'Unknown', 6: 'Voided' };
    const labels = paymentData.map(p => paymentLabels[p.payment_type] ?? p.payment_type ?? 'Unknown');
    const counts = paymentData.map(p => p.trip_count ?? p.count ?? 0);
    
    try {
        window.paymentChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: counts,
                    backgroundColor: [
                        chartColors.primary,
                        chartColors.secondary,
                        chartColors.accent,
                        chartColors.highlight,
                        chartColors.neutral
                    ],
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                ...defaultChartOptions,
                plugins: {
                    legend: {
                        position: 'right'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((context.parsed / total) * 100).toFixed(1);
                                return `${context.label}: ${context.parsed.toLocaleString()} (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error creating payment chart:', error);
    } finally {
        chartRenderStates.payment = false;
    }
}

/**
 * Create average speed by hour chart
 * @param {object} data - Speed analysis data from API
 */
function createSpeedChart(data) {
    if (chartRenderStates.speed) return;
    chartRenderStates.speed = true;
    
    const ctx = document.getElementById('chart-speed');
    if (!ctx) {
        chartRenderStates.speed = false;
        return;
    }
    
    if (window.speedChart && typeof window.speedChart.destroy === 'function') {
        window.speedChart.destroy();
        window.speedChart = null;
    }
    
    // Normalize data - API returns array of {pickup_hour, avg_speed, trip_count, ...}
    const speedData = Array.isArray(data) ? data : [];
    if (speedData.length === 0) {
        console.warn('No speed data available');
        chartRenderStates.speed = false;
        return;
    }
    
    // Extract hours and speeds
    const hours = speedData.map(d => d.pickup_hour ?? d.hour ?? 0);
    const speeds = speedData.map(d => parseFloat(d.avg_speed ?? d.avg_speed_mph ?? 0));
    
    try {
        window.speedChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: hours.map(h => {
                    if (h === 0) return '12AM';
                    if (h < 12) return `${h}AM`;
                    if (h === 12) return '12PM';
                    return `${h-12}PM`;
                }),
                datasets: [{
                    label: 'Average Speed (mph)',
                    data: speeds,
                    borderColor: chartColors.accent,
                    backgroundColor: chartColors.primary + '20',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                ...defaultChartOptions,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `${context.parsed.y.toFixed(1)} mph`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return value + ' mph';
                            }
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error creating speed chart:', error);
    } finally {
        chartRenderStates.speed = false;
    }
}

/**
 * Create weekend vs weekday comparison chart
 * @param {object} data - Weekend comparison data from API
 */
function createWeekendChart(data) {
    if (chartRenderStates.weekend) return;
    chartRenderStates.weekend = true;
    
    const ctx = document.getElementById('chart-weekend');
    if (!ctx) {
        chartRenderStates.weekend = false;
        return;
    }
    
    if (window.weekendChart && typeof window.weekendChart.destroy === 'function') {
        window.weekendChart.destroy();
        window.weekendChart = null;
    }
    
    // Normalize data - API returns array of {day_type: 'Weekend'|'Weekday', trip_count, avg_fare, ...}
    const comparisonData = Array.isArray(data) ? data : [];
    if (comparisonData.length === 0) {
        console.warn('No weekend comparison data available');
        chartRenderStates.weekend = false;
        return;
    }
    
    // Find weekend and weekday rows
    const weekendRow = comparisonData.find(d => d.day_type === 'Weekend') || {};
    const weekdayRow = comparisonData.find(d => d.day_type === 'Weekday') || {};
    
    const categories = ['Trip Count', 'Avg Fare ($)', 'Avg Distance (mi)', 'Avg Duration (min)'];
    const weekdayData = [
        weekdayRow.trip_count || 0,
        parseFloat(weekdayRow.avg_fare || 0),
        parseFloat(weekdayRow.avg_distance || 0),
        parseFloat(weekdayRow.avg_duration || 0)
    ];
    const weekendData = [
        weekendRow.trip_count || 0,
        parseFloat(weekendRow.avg_fare || 0),
        parseFloat(weekendRow.avg_distance || 0),
        parseFloat(weekendRow.avg_duration || 0)
    ];
    
    try {
        window.weekendChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: categories,
                datasets: [
                    {
                        label: 'Weekday',
                        data: weekdayData,
                        backgroundColor: chartColors.primary,
                        borderColor: chartColors.primary,
                        borderWidth: 1
                    },
                    {
                        label: 'Weekend',
                        data: weekendData,
                        backgroundColor: chartColors.secondary,
                        borderColor: chartColors.secondary,
                        borderWidth: 1
                    }
                ]
            },
            options: {
                ...defaultChartOptions,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error creating weekend chart:', error);
    } finally {
        chartRenderStates.weekend = false;
    }
}

/**
 * Create tip analysis chart
 * @param {object} data - Tip analysis data from API
 */
function createTipsChart(data) {
    if (chartRenderStates.tips) return;
    chartRenderStates.tips = true;
    
    const ctx = document.getElementById('chart-tips');
    if (!ctx) {
        chartRenderStates.tips = false;
        return;
    }
    
    if (window.tipsChart && typeof window.tipsChart.destroy === 'function') {
        window.tipsChart.destroy();
        window.tipsChart = null;
    }
    
    // Normalize data - API returns array of {payment_type, avg_tip_pct, trip_count, ...}
    const tipData = Array.isArray(data) ? data : [];
    if (tipData.length === 0) {
        console.warn('No tip data available');
        chartRenderStates.tips = false;
        return;
    }
    
    // Map payment type codes to labels
    const paymentLabels = { 1: 'Credit Card', 2: 'Cash', 3: 'No Charge', 4: 'Dispute', 5: 'Unknown', 6: 'Voided' };
    const labels = tipData.map(t => paymentLabels[t.payment_type] ?? t.payment_type ?? 'Unknown');
    const avgTips = tipData.map(t => parseFloat(t.avg_tip_pct ?? t.avg_tip ?? 0));
    
    try {
        window.tipsChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Average Tip %',
                    data: avgTips,
                    backgroundColor: chartColors.accent,
                    borderColor: chartColors.primary,
                    borderWidth: 1
                }]
            },
            options: {
                ...defaultChartOptions,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `Avg Tip: ${context.parsed.y.toFixed(1)}%`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return value + '%';
                            }
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error creating tips chart:', error);
    } finally {
        chartRenderStates.tips = false;
    }
}

/**
 * Create top routes chart
 * @param {object} data - Top routes data from API
 */
function createRoutesChart(data) {
    if (chartRenderStates.routes) return;
    chartRenderStates.routes = true;
    
    const ctx = document.getElementById('chart-routes');
    if (!ctx) {
        chartRenderStates.routes = false;
        return;
    }
    
    if (window.routesChart && typeof window.routesChart.destroy === 'function') {
        window.routesChart.destroy();
        window.routesChart = null;
    }
    
    // Validate data
    let routes = Array.isArray(data) ? data : (data.routes || []);
    if (routes.length === 0) {
        console.warn('Invalid data for routes chart, using fallback');
        routes = [{ pickup_zone: 'No Data', dropoff_zone: 'Available', trip_count: 0 }];
    }
    const labels = routes.map(r => `${r.pickup_zone} → ${r.dropoff_zone}`);
    const counts = routes.map(r => r.trip_count || 0);
    
    try {
        window.routesChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Trip Count',
                    data: counts,
                    backgroundColor: chartColors.secondary,
                    borderColor: chartColors.highlight,
                    borderWidth: 1
                }]
            },
            options: {
                ...defaultChartOptions,
                indexAxis: 'y',
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `Trips: ${context.parsed.x.toLocaleString()}`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return value.toLocaleString();
                            }
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error creating routes chart:', error);
    } finally {
        chartRenderStates.routes = false;
    }
}
