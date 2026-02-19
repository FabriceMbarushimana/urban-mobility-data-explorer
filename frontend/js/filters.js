var filterChangeCallback = null;
var debounceTimer = null;

function initFilters(onChange) {
    filterChangeCallback = onChange;

    var filterIds = [
        'filter-borough', 'filter-hour-min', 'filter-hour-max',
        'filter-dist-min', 'filter-dist-max', 'filter-fare-min', 'filter-fare-max'
    ];

    for (var i = 0; i < filterIds.length; i++) {
        var el = document.getElementById(filterIds[i]);
        if (el) {
            el.addEventListener('change', triggerChange);
            el.addEventListener('input', debounceChange);
        }
    }

    var sortEl1 = document.getElementById('sort-field');
    var sortEl2 = document.getElementById('sort-order');
    if (sortEl1) sortEl1.addEventListener('change', triggerChange);
    if (sortEl2) sortEl2.addEventListener('change', triggerChange);
}

function triggerChange() {
    if (filterChangeCallback) filterChangeCallback();
}

function debounceChange() {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(triggerChange, 400);
}

function getFilterValues() {
    var borough = document.getElementById('filter-borough').value;
    var minHour = parseInt(document.getElementById('filter-hour-min').value, 10);
    var maxHour = parseInt(document.getElementById('filter-hour-max').value, 10);
    var minDistance = parseFloat(document.getElementById('filter-dist-min').value) || 0;
    var maxDistance = parseFloat(document.getElementById('filter-dist-max').value) || 999;
    var minFare = parseFloat(document.getElementById('filter-fare-min').value) || 0;
    var maxFare = parseFloat(document.getElementById('filter-fare-max').value) || 9999;

    return {
        borough: borough,
        minHour: isNaN(minHour) ? 0 : minHour,
        maxHour: isNaN(maxHour) ? 23 : maxHour,
        minDistance: minDistance,
        maxDistance: maxDistance,
        minFare: minFare,
        maxFare: maxFare
    };
}

function getSortField() {
    return document.getElementById('sort-field').value;
}

function getSortOrder() {
    return document.getElementById('sort-order').value;
}


function sortTrips(trips, field, order) {
    if (!field || field === 'none') return trips;
    var ascending = (order === 'asc');
    return mergeSort(trips, field, ascending);
}

function mergeSort(arr, key, ascending) {
    if (arr.length <= 1) return arr;

    var mid = Math.floor(arr.length / 2);
    var left = mergeSort(arr.slice(0, mid), key, ascending);
    var right = mergeSort(arr.slice(mid), key, ascending);

    return mergeSortedArrays(left, right, key, ascending);
}

function mergeSortedArrays(left, right, key, ascending) {
    var result = [];
    var i = 0;
    var j = 0;

    while (i < left.length && j < right.length) {
        var valA = getSortValue(left[i], key);
        var valB = getSortValue(right[j], key);

        var comparison;
        if (typeof valA === 'string') {
            comparison = valA.localeCompare(valB);
        } else {
            comparison = valA - valB;
        }

        if (!ascending) comparison = -comparison;

        if (comparison <= 0) {
            result.push(left[i]);
            i++;
        } else {
            result.push(right[j]);
            j++;
        }
    }

    while (i < left.length) { result.push(left[i]); i++; }
    while (j < right.length) { result.push(right[j]); j++; }

    return result;
}

function getSortValue(obj, key) {
    if (key === 'pickupHour') return obj.pickupTime.getHours();
    return obj[key];
}
