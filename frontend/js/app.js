
var currentTrips = [];
var currentPage = 1;
var pageSize = 20;

function init() {
    initFilters(onFiltersChanged);
    onFiltersChanged();

    window.addEventListener('resize', function () {
        renderCharts(currentTrips);
    });
}

function onFiltersChanged() {
    var filters = getFilterValues();

    fetchTrips(filters).then(function (trips) {

        trips = applyLocalFilters(trips, filters);


        var sortField = getSortField();
        var sortOrder = getSortOrder();
        trips = sortTrips(trips, sortField, sortOrder);

        currentTrips = trips;
        currentPage = 1;

        updateSummaryCards(trips);
        renderCharts(trips);
        renderTable(trips);
        updateResultCount(trips.length);
    }).catch(function (err) {
        console.log('Could not load trips:', err);
        document.getElementById('result-count').textContent = 'Error loading data';
    });
}

function applyLocalFilters(trips, filters) {
    var result = [];
    for (var i = 0; i < trips.length; i++) {
        var t = trips[i];
        var hour = t.pickupTime.getHours();

        if (hour < filters.minHour || hour > filters.maxHour) continue;
        if (t.distance < filters.minDistance || t.distance > filters.maxDistance) continue;
        if (t.fareAmount < filters.minFare || t.fareAmount > filters.maxFare) continue;

        result.push(t);
    }
    return result;
}

function updateSummaryCards(trips) {
    var total = trips.length;
    var fareSum = 0;
    var distSum = 0;
    var hourCounts = [];
    for (var h = 0; h < 24; h++) hourCounts[h] = 0;

    for (var i = 0; i < trips.length; i++) {
        fareSum += trips[i].fareAmount;
        distSum += trips[i].distance;
        var hr = trips[i].pickupTime.getHours();
        hourCounts[hr]++;
    }

    var avgFare = total > 0 ? fareSum / total : 0;
    var avgDist = total > 0 ? distSum / total : 0;


    var busiestHour = 0;
    for (var h = 1; h < 24; h++) {
        if (hourCounts[h] > hourCounts[busiestHour]) {
            busiestHour = h;
        }
    }

    setText('card-total-trips', total.toLocaleString());
    setText('card-avg-fare', '$' + avgFare.toFixed(2));
    setText('card-avg-distance', avgDist.toFixed(1) + ' mi');
    setText('card-busiest-hour', formatHour(busiestHour));
}

function renderCharts(trips) {
    drawHourlyChart('chart-hourly', trips);
    drawBoroughChart('chart-borough', trips);
    drawDistanceChart('chart-distance', trips);
}

function renderTable(trips) {
    var tbody = document.getElementById('trips-tbody');
    if (!tbody) return;

    var start = (currentPage - 1) * pageSize;
    var end = Math.min(start + pageSize, trips.length);
    var pageTrips = trips.slice(start, end);

    var html = '';
    for (var i = 0; i < pageTrips.length; i++) {
        var trip = pageTrips[i];
        html += '<tr>';
        html += '<td>' + formatDateTime(trip.pickupTime) + '</td>';
        html += '<td>' + trip.pickupZone + '</td>';
        html += '<td>' + trip.dropoffZone + '</td>';
        html += '<td>' + trip.pickupBorough + '</td>';
        html += '<td>' + trip.distance.toFixed(1) + ' mi</td>';
        html += '<td>' + Math.round(trip.duration) + ' min</td>';
        html += '<td>$' + trip.fareAmount.toFixed(2) + '</td>';
        html += '<td>$' + trip.totalAmount.toFixed(2) + '</td>';
        html += '</tr>';
    }

    tbody.innerHTML = html;
    renderPagination(trips.length);
}

function renderPagination(total) {
    var container = document.getElementById('pagination');
    if (!container) return;

    var totalPages = Math.ceil(total / pageSize);
    if (totalPages <= 1) {
        container.innerHTML = '';
        return;
    }

    var html = '';
    html += '<button class="page-btn" ' + (currentPage === 1 ? 'disabled' : '') + ' onclick="goToPage(' + (currentPage - 1) + ')">« Prev</button>';

    for (var p = 1; p <= totalPages; p++) {
        if (p === currentPage) {
            html += '<button class="page-btn active">' + p + '</button>';
        } else {
            html += '<button class="page-btn" onclick="goToPage(' + p + ')">' + p + '</button>';
        }
    }

    html += '<button class="page-btn" ' + (currentPage === totalPages ? 'disabled' : '') + ' onclick="goToPage(' + (currentPage + 1) + ')">Next »</button>';
    container.innerHTML = html;
}

function goToPage(page) {
    currentPage = page;
    renderTable(currentTrips);
    document.getElementById('trips-table-section').scrollIntoView({ behavior: 'smooth' });
}

function updateResultCount(count) {
    setText('result-count', count + ' trips');
}

function formatHour(h) {
    if (h === 0) return '12:00 AM';
    if (h < 12) return h + ':00 AM';
    if (h === 12) return '12:00 PM';
    return (h - 12) + ':00 PM';
}

function formatDateTime(date) {
    var month = date.getMonth() + 1;
    var day = date.getDate();
    var hours = date.getHours();
    var minutes = date.getMinutes();
    var ampm = hours >= 12 ? 'PM' : 'AM';
    var displayHour = hours % 12 || 12;
    var minStr = minutes < 10 ? '0' + minutes : '' + minutes;
    return month + '/' + day + ' ' + displayHour + ':' + minStr + ' ' + ampm;
}

function setText(id, text) {
    var el = document.getElementById(id);
    if (el) el.textContent = text;
}

document.addEventListener('DOMContentLoaded', init);
