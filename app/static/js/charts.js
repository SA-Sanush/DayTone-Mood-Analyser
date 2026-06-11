(function () {
  const colors = {
    blue: '#2563eb',
    teal: '#0f9f8f',
    green: '#12805c',
    amber: '#f97316',
    red: '#c2413d',
    slate: '#64748b',
    grid: 'rgba(100, 116, 139, 0.18)'
  };

  const chartInstances = {};

  function chart(id, config) {
    const el = document.getElementById(id);
    if (el) {
      if (chartInstances[id]) {
        chartInstances[id].destroy();
      }
      chartInstances[id] = new Chart(el, config);
    }
  }

  Chart.defaults.font.family = 'Inter, system-ui, sans-serif';
  Chart.defaults.color = '#667085';
  Chart.defaults.plugins.legend.labels.usePointStyle = true;
  Chart.defaults.plugins.tooltip.backgroundColor = 'rgba(23, 32, 42, 0.92)';
  Chart.defaults.plugins.tooltip.padding = 12;
  Chart.defaults.plugins.tooltip.cornerRadius = 8;

  const baseScales = {
    x: { grid: { color: colors.grid }, ticks: { maxTicksLimit: 7 } },
    y: { grid: { color: colors.grid } }
  };

  const rawData = window.DAYTONE_CHARTS;

  function renderCharts(daysLimit) {
    if (!rawData) return;

    // Slice data based on selected timeframe
    const labels = rawData.labels.slice(-daysLimit);
    const mood = rawData.mood.slice(-daysLimit);
    const sleep = rawData.sleep.slice(-daysLimit);
    const stress = rawData.stress.slice(-daysLimit);
    const scatter = rawData.scatter.slice(-daysLimit);

    // Format dates to look prettier on chart X axis: e.g. "Jun 11" instead of "2026-06-11"
    const formattedLabels = labels.map(dateStr => {
      const d = new Date(dateStr);
      if (isNaN(d.getTime())) return dateStr;
      return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', timeZone: 'UTC' });
    });

    chart('moodChart', {
      type: 'line',
      data: { 
        labels: formattedLabels, 
        datasets: [{ 
          label: 'Mood', 
          data: mood, 
          borderColor: colors.blue, 
          backgroundColor: 'rgba(37, 99, 235, 0.14)', 
          fill: true, 
          pointRadius: 3, 
          pointHoverRadius: 6, 
          tension: 0.36 
        }] 
      },
      options: { 
        responsive: true, 
        maintainAspectRatio: false, 
        interaction: { intersect: false, mode: 'index' }, 
        scales: { 
          ...baseScales, 
          y: { 
            ...baseScales.y, 
            min: 1, 
            max: 5, 
            ticks: { 
              stepSize: 1, 
              callback: function(value) { 
                return {1: 'Sick', 2: 'Sad', 3: 'Anxious', 4: 'Calm', 5: 'Happy'}[value] || ''; 
              } 
            } 
          } 
        } 
      }
    });

    chart('sleepChart', {
      type: 'bar',
      data: { 
        labels: formattedLabels, 
        datasets: [{ 
          label: 'Sleep', 
          data: sleep, 
          backgroundColor: 'rgba(15, 159, 143, 0.72)', 
          borderRadius: 8 
        }] 
      },
      options: { responsive: true, maintainAspectRatio: false, scales: baseScales }
    });

    chart('stressChart', {
      type: 'line',
      data: { 
        labels: formattedLabels, 
        datasets: [{ 
          label: 'Stress', 
          data: stress, 
          borderColor: colors.red, 
          backgroundColor: 'rgba(194, 65, 61, 0.12)', 
          fill: true, 
          pointRadius: 3, 
          tension: 0.36 
        }] 
      },
      options: { 
        responsive: true, 
        maintainAspectRatio: false, 
        interaction: { intersect: false, mode: 'index' }, 
        scales: { ...baseScales, y: { ...baseScales.y, min: 1, max: 5 } } 
      }
    });

    chart('scatterChart', {
      type: 'scatter',
      data: { 
        datasets: [{ 
          label: 'Sleep vs Mood', 
          data: scatter, 
          backgroundColor: 'rgba(37, 99, 235, 0.76)', 
          pointRadius: 6, 
          pointHoverRadius: 9 
        }] 
      },
      options: { 
        responsive: true, 
        maintainAspectRatio: false, 
        scales: { 
          x: { ...baseScales.x, title: { display: true, text: 'Sleep hours' } }, 
          y: { 
            ...baseScales.y, 
            min: 1, 
            max: 5, 
            title: { display: true, text: 'Mood' }, 
            ticks: { 
              stepSize: 1, 
              callback: function(value) { 
                return {1: 'Sick', 2: 'Sad', 3: 'Anxious', 4: 'Calm', 5: 'Happy'}[value] || ''; 
              } 
            } 
          } 
        } 
      }
    });
  }

  // Initial render (default 7 days)
  renderCharts(7);

  // Render burnout donut chart (doesn't change since it is user-wide summary)
  if (rawData) {
    chart('burnoutChart', {
      type: 'doughnut',
      data: {
        labels: ['Low', 'Medium', 'High'],
        datasets: [{ 
          data: [rawData.burnout_distribution.Low, rawData.burnout_distribution.Medium, rawData.burnout_distribution.High], 
          backgroundColor: [colors.green, colors.amber, colors.red], 
          borderWidth: 0, 
          hoverOffset: 8 
        }]
      },
      options: { responsive: true, maintainAspectRatio: false, cutout: '62%' }
    });
  }

  const admin = window.DAYTONE_ADMIN;
  if (admin) {
    chart('adminBurnoutChart', {
      type: 'doughnut',
      data: {
        labels: ['Low', 'Medium', 'High'],
        datasets: [{ 
          data: [admin.burnout_distribution.Low, admin.burnout_distribution.Medium, admin.burnout_distribution.High], 
          backgroundColor: [colors.green, colors.amber, colors.red], 
          borderWidth: 0, 
          hoverOffset: 8 
        }]
      },
      options: { responsive: true, maintainAspectRatio: false, cutout: '62%' }
    });
  }

  // Expose function to update chart timeline range
  window.updateChartsTimeframe = function(days) {
    renderCharts(days);
  };
})();
