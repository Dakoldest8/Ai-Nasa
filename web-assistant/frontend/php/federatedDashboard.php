<?php
session_start();

// Check if user is logged in
if (!isset($_SESSION['username']) || !isset($_SESSION['user_id'])) {
    header("Location: loginPage.php");
    exit;
}

$USER_ID = $_SESSION['user_id'];
$AI_SERVER_URL = "http://localhost:8000";
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Federated Learning Dashboard - ECLIPSE</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            background: linear-gradient(135deg, #0b3d91 0%, #1a5bb8 100%);
            color: #fff;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
        }

        header {
            text-align: center;
            margin-bottom: 40px;
        }

        header h1 {
            font-size: 32px;
            margin-bottom: 10px;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
        }

        header p {
            font-size: 14px;
            opacity: 0.9;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }

        .stat-card {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            transition: all 0.3s ease;
        }

        .stat-card:hover {
            background: rgba(255, 255, 255, 0.15);
            transform: translateY(-5px);
        }

        .stat-label {
            font-size: 12px;
            text-transform: uppercase;
            opacity: 0.8;
            margin-bottom: 8px;
        }

        .stat-value {
            font-size: 28px;
            font-weight: bold;
            color: #00d4ff;
            margin-bottom: 5px;
        }

        .stat-change {
            font-size: 12px;
            opacity: 0.7;
        }

        .charts-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }

        .chart-container {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 10px;
            padding: 20px;
            position: relative;
        }

        .chart-title {
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid rgba(0, 212, 255, 0.5);
        }

        .chart-wrapper {
            position: relative;
            height: 300px;
            margin-bottom: 10px;
        }

        .heatmap-container {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 40px;
        }

        .heatmap-title {
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid rgba(0, 212, 255, 0.5);
        }

        .heatmap {
            overflow-x: auto;
        }

        .heatmap-table {
            border-collapse: collapse;
            width: 100%;
            font-size: 12px;
        }

        .heatmap-table th,
        .heatmap-table td {
            padding: 10px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            text-align: center;
        }

        .heatmap-table th {
            background: rgba(0, 212, 255, 0.1);
            font-weight: bold;
        }

        .heatmap-cell {
            font-weight: bold;
            color: #fff;
            border-radius: 4px;
        }

        .loading {
            text-align: center;
            padding: 40px;
            font-size: 16px;
            opacity: 0.8;
        }

        .error {
            background: rgba(255, 0, 0, 0.2);
            border: 1px solid #ff4444;
            border-radius: 10px;
            padding: 20px;
            color: #ffcccc;
            margin-bottom: 20px;
        }

        .success {
            background: rgba(0, 255, 100, 0.2);
            border: 1px solid #00ff64;
            border-radius: 10px;
            padding: 20px;
            color: #ccffdd;
            margin-bottom: 20px;
        }

        .refresh-btn {
            background: rgba(0, 212, 255, 0.3);
            border: 1px solid #00d4ff;
            color: #00d4ff;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.3s ease;
            margin-bottom: 20px;
        }

        .refresh-btn:hover {
            background: rgba(0, 212, 255, 0.5);
            transform: scale(1.05);
        }

        .back-btn {
            display: inline-block;
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            color: #fff;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            text-decoration: none;
            font-size: 14px;
            margin-bottom: 20px;
            transition: all 0.3s ease;
        }

        .back-btn:hover {
            background: rgba(255, 255, 255, 0.2);
        }
    </style>
</head>
<body>
    <div class="container">
        <a href="aiAssistant.php" class="back-btn">← Back to AI Assistant</a>

        <header>
            <h1>📊 Federated Learning Dashboard</h1>
            <p>Real-time metrics and visualizations for collaborative model training</p>
        </header>

        <button class="refresh-btn" onclick="refreshData()">🔄 Refresh Data</button>

        <div id="loading" class="loading" style="display: none;">Loading metrics...</div>
        <div id="error" class="error" style="display: none;"></div>

        <!-- Stats Grid -->
        <div class="stats-grid" id="statsGrid">
            <div class="stat-card">
                <div class="stat-label">Current Round</div>
                <div class="stat-value" id="currentRound">-</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Best Accuracy</div>
                <div class="stat-value" id="bestAccuracy">-</div>
                <div class="stat-change" id="bestRoundInfo">-</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Average Accuracy</div>
                <div class="stat-value" id="avgAccuracy">-</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Total Participants</div>
                <div class="stat-value" id="totalParticipants">-</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Completed Rounds</div>
                <div class="stat-value" id="completedRounds">-</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Avg Loss</div>
                <div class="stat-value" id="avgLoss">-</div>
            </div>
        </div>

        <!-- Charts Grid -->
        <div class="charts-grid">
            <!-- Accuracy Chart -->
            <div class="chart-container">
                <div class="chart-title">📈 Model Accuracy Over Rounds</div>
                <div class="chart-wrapper">
                    <canvas id="accuracyChart"></canvas>
                </div>
            </div>

            <!-- Convergence Chart -->
            <div class="chart-container">
                <div class="chart-title">📉 Loss Convergence</div>
                <div class="chart-wrapper">
                    <canvas id="convergenceChart"></canvas>
                </div>
            </div>
        </div>

        <!-- Heatmap -->
        <div class="heatmap-container">
            <div class="heatmap-title">🔥 Participant Accuracy Heatmap (Rounds vs Participants)</div>
            <div class="heatmap" id="heatmapContainer">
                <p style="text-align: center; opacity: 0.7;">No heatmap data available yet</p>
            </div>
        </div>
    </div>

    <script>
        let accuracyChart = null;
        let convergenceChart = null;

        async function fetchMetrics() {
            try {
                const response = await fetch('<?php echo $AI_SERVER_URL; ?>/federated/metrics/all');
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const data = await response.json();
                
                if (data.status === 'success') {
                    displayMetrics(data.metrics);
                    return data.metrics;
                } else {
                    showError('Failed to fetch metrics: ' + data.error);
                }
            } catch (error) {
                showError('Error fetching metrics: ' + error.message);
                console.error('Error:', error);
            }
        }

        function displayMetrics(metrics) {
            const summary = metrics.summary;

            // Update stats
            document.getElementById('currentRound').textContent = summary.current_round || 0;
            document.getElementById('bestAccuracy').textContent = 
                (summary.best_accuracy * 100).toFixed(2) + '%';
            document.getElementById('avgAccuracy').textContent = 
                (summary.average_accuracy * 100).toFixed(2) + '%';
            document.getElementById('totalParticipants').textContent = summary.total_participants || 0;
            document.getElementById('completedRounds').textContent = summary.completed_rounds || 0;
            document.getElementById('avgLoss').textContent = 
                summary.average_loss ? summary.average_loss.toFixed(4) : '-';
            document.getElementById('bestRoundInfo').textContent = 
                `Round ${summary.best_round}`;

            // Update charts
            if (metrics.accuracy_history && metrics.accuracy_history.length > 0) {
                updateAccuracyChart(metrics.accuracy_history);
            }

            if (metrics.convergence_data && metrics.convergence_data.length > 0) {
                updateConvergenceChart(metrics.convergence_data);
            }

            if (metrics.heatmap_data && metrics.heatmap_data.data.length > 0) {
                displayHeatmap(metrics.heatmap_data);
            }

            hideLoading();
        }

        function updateAccuracyChart(data) {
            const ctx = document.getElementById('accuracyChart').getContext('2d');
            
            const chartData = {
                labels: data.map(d => `Round ${d.round}`),
                datasets: [{
                    label: 'Model Accuracy',
                    data: data.map(d => (d.accuracy * 100).toFixed(2)),
                    borderColor: '#00d4ff',
                    backgroundColor: 'rgba(0, 212, 255, 0.1)',
                    borderWidth: 2,
                    tension: 0.4,
                    fill: true,
                    pointBackgroundColor: '#00d4ff',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointRadius: 5,
                    pointHoverRadius: 7
                }]
            };

            if (accuracyChart) {
                accuracyChart.destroy();
            }

            accuracyChart = new Chart(ctx, {
                type: 'line',
                data: chartData,
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            labels: {
                                color: '#fff'
                            }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 100,
                            ticks: {
                                color: 'rgba(255, 255, 255, 0.7)',
                                callback: function(value) {
                                    return value + '%';
                                }
                            },
                            grid: {
                                color: 'rgba(255, 255, 255, 0.1)'
                            }
                        },
                        x: {
                            ticks: {
                                color: 'rgba(255, 255, 255, 0.7)'
                            },
                            grid: {
                                color: 'rgba(255, 255, 255, 0.1)'
                            }
                        }
                    }
                }
            });
        }

        function updateConvergenceChart(data) {
            const ctx = document.getElementById('convergenceChart').getContext('2d');
            
            const chartData = {
                labels: data.map(d => `Round ${d.round}`),
                datasets: [{
                    label: 'Loss',
                    data: data.map(d => d.loss),
                    borderColor: '#ff6b6b',
                    backgroundColor: 'rgba(255, 107, 107, 0.1)',
                    borderWidth: 2,
                    tension: 0.4,
                    fill: true,
                    pointBackgroundColor: '#ff6b6b',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointRadius: 5,
                    pointHoverRadius: 7
                }]
            };

            if (convergenceChart) {
                convergenceChart.destroy();
            }

            convergenceChart = new Chart(ctx, {
                type: 'line',
                data: chartData,
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            labels: {
                                color: '#fff'
                            }
                        }
                    },
                    scales: {
                        y: {
                            ticks: {
                                color: 'rgba(255, 255, 255, 0.7)'
                            },
                            grid: {
                                color: 'rgba(255, 255, 255, 0.1)'
                            }
                        },
                        x: {
                            ticks: {
                                color: 'rgba(255, 255, 255, 0.7)'
                            },
                            grid: {
                                color: 'rgba(255, 255, 255, 0.1)'
                            }
                        }
                    }
                }
            });
        }

        function displayHeatmap(heatmapData) {
            const container = document.getElementById('heatmapContainer');
            
            if (!heatmapData.data || heatmapData.data.length === 0) {
                container.innerHTML = '<p style="text-align: center; opacity: 0.7;">No heatmap data available</p>';
                return;
            }

            let html = '<table class="heatmap-table"><thead><tr><th>Device / Round</th>';
            
            // Header row with round numbers
            heatmapData.rounds.forEach(round => {
                html += `<th>R${round}</th>`;
            });
            html += '</tr></thead><tbody>';

            // Data rows
            heatmapData.participants.forEach((participant, idx) => {
                html += `<tr><th style="text-align: left; max-width: 150px; word-break: break-all;">${participant}</th>`;
                
                heatmapData.data[idx].forEach(accuracy => {
                    if (accuracy !== null) {
                        const percentage = (accuracy * 100).toFixed(0);
                        const hue = (percentage * 1.2) % 360; // Green to red spectrum
                        const color = `hsl(${120 - (percentage * 1.2)}, 100%, 50%)`;
                        html += `<td><div class="heatmap-cell" style="background: ${color};">${percentage}%</div></td>`;
                    } else {
                        html += `<td style="opacity: 0.3;">-</td>`;
                    }
                });
                
                html += '</tr>';
            });

            html += '</tbody></table>';
            container.innerHTML = html;
        }

        function showLoading() {
            document.getElementById('loading').style.display = 'block';
            document.getElementById('error').style.display = 'none';
        }

        function hideLoading() {
            document.getElementById('loading').style.display = 'none';
        }

        function showError(message) {
            const errorDiv = document.getElementById('error');
            errorDiv.textContent = message;
            errorDiv.style.display = 'block';
        }

        function refreshData() {
            showLoading();
            fetchMetrics();
        }

        // Initial load
        window.addEventListener('load', () => {
            showLoading();
            fetchMetrics();
        });

        // Auto-refresh every 30 seconds
        setInterval(fetchMetrics, 30000);
    </script>
</body>
</html>