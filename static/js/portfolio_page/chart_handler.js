document.addEventListener('DOMContentLoaded', function() {
  // Get chart data from Flask
  const chartData = window.chartData;

  // Get the canvas context
  const ctx = document.getElementById('performanceChart').getContext('2d');

  // Set initial period to 1M (matches the button with teal background)
  let currentPeriod = '1M';

  // Create chart
  const performanceChart = new Chart(ctx, {
    type: 'line',
    data: {
      datasets: [
        {
          label: 'Portfolio Value',
          data: chartData[currentPeriod].map(point => ({
            x: point.x,
            y: point.total_value
          })),
          borderColor: '#2DD4BF', // teal-400
          backgroundColor: 'rgba(45, 212, 191, 0.1)',
          borderWidth: 2,
          pointRadius: 1,
          pointHoverRadius: 5,
          fill: true,
          tension: 0.4
        },
        {
          label: 'Total Investment',
          data: chartData[currentPeriod].map(point => ({
            x: point.x,
            y: point.total_investment
          })),
          borderColor: '#6B7280', // gray-500
          backgroundColor: 'rgba(107, 114, 128, 0.1)',
          borderWidth: 1.5,
          pointRadius: 0,
          pointHoverRadius: 4,
          borderDash: [5, 5],
          fill: false
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: {
        mode: 'index',
        intersect: false,
      },
      plugins: {
        tooltip: {
          callbacks: {
            label: function(context) {
              const pointIndex = context.dataIndex;
              const datasetLabel = context.dataset.label;
              const value = context.parsed.y;

              if (datasetLabel === 'Portfolio Value') {
                const profitLoss = chartData[currentPeriod][pointIndex].profit_loss;
                const profitLossPercentage = chartData[currentPeriod][pointIndex].profit_loss_percentage;
                const sign = profitLoss >= 0 ? '+' : '';

                return [
                  `${datasetLabel}: $${value.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}`,
                  `P/L: ${sign}$${profitLoss.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})} (${sign}${profitLossPercentage.toFixed(2)}%)`
                ];
              }

              return `${datasetLabel}: $${value.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
            },
            title: function(context) {
              // Format the date/time
              const date = new Date(context[0].parsed.x);
              return date.toLocaleString();
            }
          }
        },
        legend: {
          labels: {
            color: '#D1D5DB', // gray-300
            font: {
              family: 'system-ui, sans-serif'
            }
          }
        }
      },
      scales: {
        x: {
          type: 'time',
          time: {
            unit: getTimeUnit(currentPeriod)
          },
          grid: {
            color: 'rgba(75, 85, 99, 0.3)' // gray-600 with transparency
          },
          ticks: {
            color: '#9CA3AF' // gray-400
          }
        },
        y: {
          beginAtZero: false,
          grid: {
            color: 'rgba(75, 85, 99, 0.3)' // gray-600 with transparency
          },
          ticks: {
            color: '#9CA3AF', // gray-400
            callback: function(value) {
              return '$' + value.toLocaleString();
            }
          }
        }
      }
    }
  });

  // Helper function to determine time unit based on period
  function getTimeUnit(period) {
    switch(period) {
      case '1D': return 'hour';
      case '1W': return 'day';
      case '1M': return 'day';
      case '3M': return 'week';
      case '1Y': return 'month';
      case 'All': return 'month';
      default: return 'day';
    }
  }

  // Update chart data when period buttons are clicked
  document.querySelectorAll('.period-btn').forEach(button => {
    button.addEventListener('click', function() {
      // Update active button styling
      document.querySelectorAll('.period-btn').forEach(btn => {
        btn.classList.remove('bg-teal-600', 'hover:bg-teal-700', 'active');
        btn.classList.add('bg-gray-700', 'hover:bg-gray-600');
      });
      this.classList.remove('bg-gray-700', 'hover:bg-gray-600');
      this.classList.add('bg-teal-600', 'hover:bg-teal-700', 'active');

      // Get selected period
      currentPeriod = this.getAttribute('data-period');

      // Update chart data
      performanceChart.data.datasets[0].data = chartData[currentPeriod].map(point => ({
        x: point.x,
        y: point.total_value
      }));

      performanceChart.data.datasets[1].data = chartData[currentPeriod].map(point => ({
        x: point.x,
        y: point.total_investment
      }));

      // Update time unit
      performanceChart.options.scales.x.time.unit = getTimeUnit(currentPeriod);

      // Update chart
      performanceChart.update();
    });
  });
});