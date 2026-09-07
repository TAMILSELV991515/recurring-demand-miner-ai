function renderMonthlyTrendChart(canvasId, labels, dataPoints) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels || ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
            datasets: [{
                label: 'Monthly Support Demand',
                data: dataPoints || [420, 380, 450, 410, 390, 480, 460, 430, 410, 395, 380, 360],
                borderColor: '#38bdf8',
                backgroundColor: 'rgba(56, 189, 248, 0.15)',
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointRadius: 4,
                pointBackgroundColor: '#6366f1'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                x: { grid: { display: false }, ticks: { color: '#94a3b8' } },
                y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94a3b8' } }
            }
        }
    });
}

function renderChannelChart(canvasId, channelData) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;
    
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: Object.keys(channelData || { 'Email': 40, 'Chat': 30, 'Phone': 18, 'Portal': 12 }),
            datasets: [{
                data: Object.values(channelData || { 'Email': 40, 'Chat': 30, 'Phone': 18, 'Portal': 12 }),
                backgroundColor: ['#38bdf8', '#6366f1', '#a855f7', '#34d399'],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'bottom', labels: { color: '#94a3b8', font: { size: 12 } } }
            },
            cutout: '70%'
        }
    });
}

function renderBenchmarkChart(canvasId, benchmarkData) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;
    
    const models = Object.keys(benchmarkData);
    const precision = models.map(m => benchmarkData[m].precision);
    const recall = models.map(m => benchmarkData[m].recall);
    const f1 = models.map(m => benchmarkData[m].f1_score);
    const accuracy = models.map(m => benchmarkData[m].accuracy);
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: models,
            datasets: [
                { label: 'Precision %', data: precision, backgroundColor: '#38bdf8' },
                { label: 'Recall %', data: recall, backgroundColor: '#6366f1' },
                { label: 'F1 Score %', data: f1, backgroundColor: '#a855f7' },
                { label: 'Accuracy %', data: accuracy, backgroundColor: '#34d399' }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'top', labels: { color: '#94a3b8' } }
            },
            scales: {
                x: { grid: { display: false }, ticks: { color: '#94a3b8' } },
                y: { min: 40, max: 100, grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94a3b8' } }
            }
        }
    });
}
