
var chartColors = {
    bar: '#2d5f2d',
    barAlt: '#c4553a',
    grid: '#e0ddd4',
    text: '#1a1a1a',
    textLight: '#6b6b6b'
};


function drawHourlyChart(canvasId, trips) {
    var canvas = document.getElementById(canvasId);
    if (!canvas) return;

    var ctx = canvas.getContext('2d');
    var w = canvas.offsetWidth;
    var h = canvas.offsetHeight;
    canvas.width = w;
    canvas.height = h;


    var hourCounts = [];
    for (var i = 0; i < 24; i++) hourCounts[i] = 0;
    for (var t = 0; t < trips.length; t++) {
        var hour = trips[t].pickupTime.getHours();
        hourCounts[hour]++;
    }

    var maxCount = 1;
    for (var i = 0; i < 24; i++) {
        if (hourCounts[i] > maxCount) maxCount = hourCounts[i];
    }

    var pad = { top: 20, right: 20, bottom: 40, left: 45 };
    var chartW = w - pad.left - pad.right;
    var chartH = h - pad.top - pad.bottom;
    var barW = chartW / 24 - 3;


    ctx.strokeStyle = chartColors.grid;
    ctx.lineWidth = 1;
    for (var g = 0; g <= 4; g++) {
        var y = pad.top + (chartH / 4) * g;
        ctx.beginPath();
        ctx.moveTo(pad.left, y);
        ctx.lineTo(w - pad.right, y);
        ctx.stroke();

        ctx.fillStyle = chartColors.textLight;
        ctx.font = '11px sans-serif';
        ctx.textAlign = 'right';
        ctx.fillText(Math.round(maxCount - (maxCount / 4) * g), pad.left - 8, y + 4);
    }


    for (var i = 0; i < 24; i++) {
        var barH = (hourCounts[i] / maxCount) * chartH;
        var x = pad.left + i * (chartW / 24) + 1.5;
        var y = pad.top + chartH - barH;

        var isPeak = (i >= 7 && i <= 9) || (i >= 17 && i <= 19);
        ctx.fillStyle = isPeak ? chartColors.barAlt : chartColors.bar;

        ctx.beginPath();
        ctx.rect(x, y, barW, barH);
        ctx.fill();

        if (i % 2 === 0) {
            ctx.fillStyle = chartColors.textLight;
            ctx.font = '10px sans-serif';
            ctx.textAlign = 'center';
            var label = i === 0 ? '12a' : i < 12 ? i + 'a' : i === 12 ? '12p' : (i - 12) + 'p';
            ctx.fillText(label, x + barW / 2, h - pad.bottom + 15);
        }
    }


    ctx.strokeStyle = chartColors.text;
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(pad.left, pad.top + chartH);
    ctx.lineTo(w - pad.right, pad.top + chartH);
    ctx.stroke();
}


function drawBoroughChart(canvasId, trips) {
    var canvas = document.getElementById(canvasId);
    if (!canvas) return;

    var ctx = canvas.getContext('2d');
    var w = canvas.offsetWidth;
    var h = canvas.offsetHeight;
    canvas.width = w;
    canvas.height = h;

    var boroughData = {};
    for (var t = 0; t < trips.length; t++) {
        var b = trips[t].pickupBorough;
        if (!boroughData[b]) boroughData[b] = { total: 0, count: 0 };
        boroughData[b].total += trips[t].fareAmount;
        boroughData[b].count++;
    }

    var boroughs = [];
    var keys = Object.keys(boroughData);
    for (var k = 0; k < keys.length; k++) {
        var name = keys[k];
        boroughs.push({
            name: name,
            avg: boroughData[name].total / boroughData[name].count
        });
    }


    for (var i = 0; i < boroughs.length - 1; i++) {
        for (var j = i + 1; j < boroughs.length; j++) {
            if (boroughs[j].avg > boroughs[i].avg) {
                var temp = boroughs[i];
                boroughs[i] = boroughs[j];
                boroughs[j] = temp;
            }
        }
    }

    if (boroughs.length === 0) return;
    var maxAvg = boroughs[0].avg;

    var pad = { top: 15, right: 70, bottom: 15, left: 110 };
    var chartW = w - pad.left - pad.right;
    var chartH = h - pad.top - pad.bottom;
    var barHeight = Math.min(30, chartH / boroughs.length - 8);

    for (var i = 0; i < boroughs.length; i++) {
        var barW = (boroughs[i].avg / maxAvg) * chartW;
        var y = pad.top + i * (chartH / boroughs.length) + (chartH / boroughs.length - barHeight) / 2;

        ctx.fillStyle = i === 0 ? chartColors.barAlt : chartColors.bar;
        ctx.beginPath();
        ctx.rect(pad.left, y, barW, barHeight);
        ctx.fill();

        ctx.fillStyle = chartColors.text;
        ctx.font = '12px sans-serif';
        ctx.textAlign = 'right';
        ctx.fillText(boroughs[i].name, pad.left - 10, y + barHeight / 2 + 4);

        ctx.fillStyle = chartColors.textLight;
        ctx.font = '11px sans-serif';
        ctx.textAlign = 'left';
        ctx.fillText('$' + boroughs[i].avg.toFixed(2), pad.left + barW + 8, y + barHeight / 2 + 4);
    }
}


function drawDistanceChart(canvasId, trips) {
    var canvas = document.getElementById(canvasId);
    if (!canvas) return;

    var ctx = canvas.getContext('2d');
    var w = canvas.offsetWidth;
    var h = canvas.offsetHeight;
    canvas.width = w;
    canvas.height = h;


    var bucketCount = 16;
    var buckets = [];
    for (var i = 0; i < bucketCount; i++) buckets[i] = 0;
    for (var t = 0; t < trips.length; t++) {
        var bucket = Math.min(Math.floor(trips[t].distance), bucketCount - 1);
        buckets[bucket]++;
    }

    var maxCount = 1;
    for (var i = 0; i < bucketCount; i++) {
        if (buckets[i] > maxCount) maxCount = buckets[i];
    }

    var pad = { top: 20, right: 20, bottom: 40, left: 45 };
    var chartW = w - pad.left - pad.right;
    var chartH = h - pad.top - pad.bottom;
    var barW = chartW / bucketCount - 2;


    ctx.strokeStyle = chartColors.grid;
    ctx.lineWidth = 1;
    for (var g = 0; g <= 4; g++) {
        var y = pad.top + (chartH / 4) * g;
        ctx.beginPath();
        ctx.moveTo(pad.left, y);
        ctx.lineTo(w - pad.right, y);
        ctx.stroke();

        ctx.fillStyle = chartColors.textLight;
        ctx.font = '11px sans-serif';
        ctx.textAlign = 'right';
        ctx.fillText(Math.round(maxCount - (maxCount / 4) * g), pad.left - 8, y + 4);
    }


    for (var i = 0; i < bucketCount; i++) {
        var barH = (buckets[i] / maxCount) * chartH;
        var x = pad.left + i * (chartW / bucketCount) + 1;
        var y = pad.top + chartH - barH;


        var ratio = i / (bucketCount - 1);
        ctx.fillStyle = mixColor(chartColors.bar, chartColors.barAlt, ratio);

        ctx.beginPath();
        ctx.rect(x, y, barW, barH);
        ctx.fill();

        if (i % 2 === 0 || i === bucketCount - 1) {
            ctx.fillStyle = chartColors.textLight;
            ctx.font = '10px sans-serif';
            ctx.textAlign = 'center';
            var distLabel = i === bucketCount - 1 ? i + '+' : i + '';
            ctx.fillText(distLabel + ' mi', x + barW / 2, h - pad.bottom + 15);
        }
    }


    ctx.strokeStyle = chartColors.text;
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(pad.left, pad.top + chartH);
    ctx.lineTo(w - pad.right, pad.top + chartH);
    ctx.stroke();
}

function mixColor(hex1, hex2, ratio) {
    var r1 = parseInt(hex1.slice(1, 3), 16);
    var g1 = parseInt(hex1.slice(3, 5), 16);
    var b1 = parseInt(hex1.slice(5, 7), 16);
    var r2 = parseInt(hex2.slice(1, 3), 16);
    var g2 = parseInt(hex2.slice(3, 5), 16);
    var b2 = parseInt(hex2.slice(5, 7), 16);

    var r = Math.round(r1 + (r2 - r1) * ratio);
    var g = Math.round(g1 + (g2 - g1) * ratio);
    var b = Math.round(b1 + (b2 - b1) * ratio);

    return 'rgb(' + r + ',' + g + ',' + b + ')';
}
