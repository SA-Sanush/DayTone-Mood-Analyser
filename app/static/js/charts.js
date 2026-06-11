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

  function chart(id, config) {
    const el = document.getElementById(id);
    if (el) new Chart(el, config);
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

  const data = window.DAYTONE_CHARTS;
  if (data) {
    chart('moodChart', {
      type: 'line',
      data: { labels: data.labels, datasets: [{ label: 'Mood', data: data.mood, borderColor: colors.blue, backgroundColor: 'rgba(37, 99, 235, 0.14)', fill: true, pointRadius: 3, pointHoverRadius: 6, tension: 0.36 }] },
      options: { responsive: true, maintainAspectRatio: false, interaction: { intersect: false, mode: 'index' }, scales: { ...baseScales, y: { ...baseScales.y, min: 1, max: 5, ticks: { stepSize: 1, callback: function(value) { return {1: 'Sick', 2: 'Sad', 3: 'Anxious', 4: 'Calm', 5: 'Happy'}[value] || ''; } } } } }
    });
    chart('sleepChart', {
      type: 'bar',
      data: { labels: data.labels, datasets: [{ label: 'Sleep', data: data.sleep, backgroundColor: 'rgba(15, 159, 143, 0.72)', borderRadius: 8 }] },
      options: { responsive: true, maintainAspectRatio: false, scales: baseScales }
    });
    chart('stressChart', {
      type: 'line',
      data: { labels: data.labels, datasets: [{ label: 'Stress', data: data.stress, borderColor: colors.red, backgroundColor: 'rgba(194, 65, 61, 0.12)', fill: true, pointRadius: 3, tension: 0.36 }] },
      options: { responsive: true, maintainAspectRatio: false, interaction: { intersect: false, mode: 'index' }, scales: { ...baseScales, y: { ...baseScales.y, min: 1, max: 5 } } }
    });
    chart('burnoutChart', {
      type: 'doughnut',
      data: {
        labels: ['Low', 'Medium', 'High'],
        datasets: [{ data: [data.burnout_distribution.Low, data.burnout_distribution.Medium, data.burnout_distribution.High], backgroundColor: [colors.green, colors.amber, colors.red], borderWidth: 0, hoverOffset: 8 }]
      },
      options: { responsive: true, maintainAspectRatio: false, cutout: '62%' }
    });
    chart('scatterChart', {
      type: 'scatter',
      data: { datasets: [{ label: 'Sleep vs Mood', data: data.scatter, backgroundColor: 'rgba(37, 99, 235, 0.76)', pointRadius: 6, pointHoverRadius: 9 }] },
      options: { responsive: true, maintainAspectRatio: false, scales: { x: { ...baseScales.x, title: { display: true, text: 'Sleep hours' } }, y: { ...baseScales.y, min: 1, max: 5, title: { display: true, text: 'Mood' }, ticks: { stepSize: 1, callback: function(value) { return {1: 'Sick', 2: 'Sad', 3: 'Anxious', 4: 'Calm', 5: 'Happy'}[value] || ''; } } } } }
    });
  }

  const admin = window.DAYTONE_ADMIN;
  if (admin) {
    chart('adminBurnoutChart', {
      type: 'doughnut',
      data: {
        labels: ['Low', 'Medium', 'High'],
        datasets: [{ data: [admin.burnout_distribution.Low, admin.burnout_distribution.Medium, admin.burnout_distribution.High], backgroundColor: [colors.green, colors.amber, colors.red], borderWidth: 0, hoverOffset: 8 }]
      },
      options: { responsive: true, maintainAspectRatio: false, cutout: '62%' }
    });
  }
})();
