(function () {
  'use strict';

  function isDarkMode() {
    const theme = document.documentElement.getAttribute('data-theme');
    return theme === 'nocturne' || theme === 'dark';
  }

  function getThemeColors() {
    const dark = isDarkMode();
    return {
      mood: '#0ea5e9',
      moodBg: dark ? 'rgba(14, 165, 233, 0.18)' : 'rgba(14, 165, 233, 0.12)',
      sleep: '#14b8a6',
      sleepBg: dark ? 'rgba(20, 184, 166, 0.75)' : 'rgba(20, 184, 166, 0.85)',
      stress: '#f43f5e',
      stressBg: dark ? 'rgba(244, 63, 94, 0.15)' : 'rgba(244, 63, 94, 0.12)',
      scatter: '#6366f1',
      scatterBg: dark ? 'rgba(99, 102, 241, 0.8)' : 'rgba(99, 102, 241, 0.75)',
      donutLow: '#10b981',
      donutMedium: '#f59e0b',
      donutHigh: '#ef4444',
      text: dark ? '#cbd5e1' : '#64748b',
      grid: dark ? 'rgba(255, 255, 255, 0.07)' : 'rgba(15, 23, 42, 0.06)',
      tooltipBg: dark ? 'rgba(15, 23, 42, 0.95)' : 'rgba(255, 255, 255, 0.95)',
      tooltipTitle: dark ? '#f8fafc' : '#0f172a',
      tooltipBody: dark ? '#cbd5e1' : '#334155'
    };
  }

  const chartInstances = {};

  function chart(id, config) {
    const el = document.getElementById(id);
    if (!el) return;
    if (chartInstances[id]) {
      chartInstances[id].destroy();
    }
    chartInstances[id] = new Chart(el, config);
  }

  let currentDaysLimit = 7;
  const rawData = window.DAYTONE_CHARTS;

  function renderCharts(daysLimit) {
    if (!rawData) return;
    currentDaysLimit = daysLimit;
    const colors = getThemeColors();

    Chart.defaults.font.family = 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
    Chart.defaults.font.size = 11;
    Chart.defaults.color = colors.text;
    Chart.defaults.plugins.legend.labels.usePointStyle = true;
    Chart.defaults.plugins.legend.labels.boxWidth = 8;
    Chart.defaults.plugins.tooltip.backgroundColor = colors.tooltipBg;
    Chart.defaults.plugins.tooltip.titleColor = colors.tooltipTitle;
    Chart.defaults.plugins.tooltip.bodyColor = colors.tooltipBody;
    Chart.defaults.plugins.tooltip.borderColor = isDarkMode() ? 'rgba(255, 255, 255, 0.15)' : 'rgba(15, 23, 42, 0.1)';
    Chart.defaults.plugins.tooltip.borderWidth = 1;
    Chart.defaults.plugins.tooltip.padding = 10;
    Chart.defaults.plugins.tooltip.cornerRadius = 10;

    const baseScales = {
      x: { 
        grid: { color: colors.grid, drawBorder: false }, 
        ticks: { color: colors.text, maxTicksLimit: 7 } 
      },
      y: { 
        grid: { color: colors.grid, drawBorder: false },
        ticks: { color: colors.text }
      }
    };

    // Slice data based on selected timeframe
    const labels = rawData.labels.slice(-daysLimit);
    const mood = rawData.mood.slice(-daysLimit);
    const sleep = rawData.sleep.slice(-daysLimit);
    const stress = rawData.stress.slice(-daysLimit);
    const scatter = rawData.scatter.slice(-daysLimit);

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
          borderColor: colors.mood, 
          backgroundColor: colors.moodBg, 
          fill: true, 
          pointRadius: 4, 
          pointHoverRadius: 7, 
          pointBackgroundColor: colors.mood,
          tension: 0.35,
          borderWidth: 2.5
        }] 
      },
      options: { 
        responsive: true, 
        maintainAspectRatio: false, 
        plugins: {
          legend: { display: false }
        },
        interaction: { intersect: false, mode: 'index' }, 
        scales: { 
          ...baseScales, 
          y: { 
            ...baseScales.y, 
            min: 1, 
            max: 5, 
            ticks: { 
              color: colors.text,
              stepSize: 1, 
              callback: function(value) { 
                return {1: 'Sick', 2: 'Sad', 3: 'Anx', 4: 'Calm', 5: 'Happy'}[value] || ''; 
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
          label: 'Sleep Hours', 
          data: sleep, 
          backgroundColor: colors.sleepBg, 
          borderColor: colors.sleep,
          borderWidth: 1,
          borderRadius: 8 
        }] 
      },
      options: { 
        responsive: true, 
        maintainAspectRatio: false, 
        plugins: { legend: { display: false } },
        scales: baseScales 
      }
    });

    chart('stressChart', {
      type: 'line',
      data: { 
        labels: formattedLabels, 
        datasets: [{ 
          label: 'Stress Level', 
          data: stress, 
          borderColor: colors.stress, 
          backgroundColor: colors.stressBg, 
          fill: true, 
          pointRadius: 4, 
          pointHoverRadius: 7, 
          pointBackgroundColor: colors.stress,
          tension: 0.35,
          borderWidth: 2.5
        }] 
      },
      options: { 
        responsive: true, 
        maintainAspectRatio: false, 
        plugins: { legend: { display: false } },
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
          backgroundColor: colors.scatterBg, 
          borderColor: colors.scatter,
          borderWidth: 1.5,
          pointRadius: 6, 
          pointHoverRadius: 9 
        }] 
      },
      options: { 
        responsive: true, 
        maintainAspectRatio: false, 
        plugins: { legend: { display: false } },
        scales: { 
          x: { ...baseScales.x, title: { display: true, text: 'Sleep (hours)', color: colors.text } }, 
          y: { 
            ...baseScales.y, 
            min: 1, 
            max: 5, 
            title: { display: true, text: 'Mood', color: colors.text }, 
            ticks: { 
              color: colors.text,
              stepSize: 1, 
              callback: function(value) { 
                return {1: 'Sick', 2: 'Sad', 3: 'Anx', 4: 'Calm', 5: 'Happy'}[value] || ''; 
              } 
            } 
          } 
        } 
      }
    });
  }

  function renderBurnout() {
    const colors = getThemeColors();

    if (rawData && rawData.burnout_distribution) {
      chart('burnoutChart', {
        type: 'doughnut',
        data: {
          labels: ['Low', 'Medium', 'High'],
          datasets: [{ 
            data: [rawData.burnout_distribution.Low, rawData.burnout_distribution.Medium, rawData.burnout_distribution.High], 
            backgroundColor: [colors.donutLow, colors.donutMedium, colors.donutHigh], 
            borderWidth: 0, 
            hoverOffset: 6 
          }]
        },
        options: { 
          responsive: true, 
          maintainAspectRatio: false, 
          cutout: '72%',
          plugins: {
            legend: {
              position: 'top',
              labels: {
                boxWidth: 8,
                padding: 10,
                color: colors.text,
                font: { size: 11 }
              }
            }
          }
        }
      });
    }

    const admin = window.DAYTONE_ADMIN;
    if (admin && admin.burnout_distribution) {
      chart('adminBurnoutChart', {
        type: 'doughnut',
        data: {
          labels: ['Low', 'Medium', 'High'],
          datasets: [{ 
            data: [admin.burnout_distribution.Low, admin.burnout_distribution.Medium, admin.burnout_distribution.High], 
            backgroundColor: [colors.donutLow, colors.donutMedium, colors.donutHigh], 
            borderWidth: 0, 
            hoverOffset: 6 
          }]
        },
        options: { 
          responsive: true, 
          maintainAspectRatio: false, 
          cutout: '72%',
          plugins: {
            legend: {
              position: 'top',
              labels: {
                boxWidth: 8,
                padding: 10,
                color: colors.text,
                font: { size: 11 }
              }
            }
          }
        }
      });
    }
  }

  // Initial render
  renderCharts(7);
  renderBurnout();

  // Expose function to update chart timeline range
  window.updateChartsTimeframe = function(days) {
    renderCharts(days);
  };

  // Listen for darkmode toggle to update chart themes
  document.getElementById('darkToggle')?.addEventListener('click', () => {
    setTimeout(() => {
      renderCharts(currentDaysLimit);
      renderBurnout();
    }, 100);
  });
})();
