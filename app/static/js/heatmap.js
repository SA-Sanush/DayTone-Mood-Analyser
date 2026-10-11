(function () {
  const target = document.getElementById('heatmap');
  if (!target) return;

  const tooltip = document.getElementById('heatmapTooltip');
  const detailCard = document.getElementById('heatmapDetailCard');
  const detailDefault = document.getElementById('heatmapDetailDefault');
  const detailContent = document.getElementById('heatmapDetailContent');
  const loader = document.getElementById('heatmapLoader');
  const yearSelector = document.getElementById('heatmapYearSelector');
  const legendItems = document.querySelectorAll('.heatmap-legend .legend-item');

  let rows = [];
  const now = new Date();
  let selectedYear = now.getFullYear();
  let selectedCellData = null;

  function isDarkMode() {
    const theme = document.documentElement.getAttribute('data-theme');
    return theme === 'dark' || theme === 'nocturne' || document.documentElement.classList.contains('dark');
  }

  function getColors() {
    const dark = isDarkMode();
    return [
      dark ? 'rgba(255, 255, 255, 0.08)' : 'rgba(255, 255, 255, 0.28)', // 0: unlogged frosted glass
      dark ? 'rgba(244, 63, 94, 0.85)' : '#fb7185',  // 1: sick
      dark ? 'rgba(249, 115, 22, 0.85)' : '#fb923c', // 2: sad
      dark ? 'rgba(245, 158, 11, 0.85)' : '#fbbf24', // 3: anxious
      dark ? 'rgba(20, 184, 166, 0.85)' : '#2dd4bf', // 4: calm
      dark ? 'rgba(16, 185, 129, 0.85)' : '#34d399'  // 5: happy
    ];
  }

  const moodLabels = {
    1: '🤒 Sick',
    2: '😢 Sad',
    3: '😰 Anxious',
    4: '😌 Calm',
    5: '😊 Happy'
  };

  async function loadData(year) {
    if (loader) loader.classList.remove('d-none');
    try {
      const response = await fetch(`/api/heatmap?year=${year}`);
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      rows = await response.json();
    } catch (err) {
      console.error("Failed to load heatmap data:", err);
      target.textContent = "Could not load heatmap data. Please try again later.";
      rows = [];
    } finally {
      if (loader) loader.classList.add('d-none');
    }
  }

  function renderHeatmap(year) {
    target.innerHTML = '';
    
    const colors = getColors();
    const byDate = new Map(rows.map((row) => [row.date, row]));
    const start = new Date(year, 0, 1);
    const end = new Date(year, 11, 31);
    const cell = 14;
    const gap = 3;
    const width = 54 * (cell + gap);
    const height = 7 * (cell + gap) + 24;

    const svg = d3.select(target).append('svg')
      .attr('viewBox', `0 0 ${width} ${height}`)
      .attr('role', 'img')
      .attr('aria-label', `Mood heatmap for the year ${year}`);
      
    const days = d3.timeDays(start, d3.timeDay.offset(end, 1));

    const cells = svg.selectAll('rect')
      .data(days)
      .join('rect')
      .attr('class', 'heat-cell')
      .attr('width', cell)
      .attr('height', cell)
      .attr('rx', 3)
      .attr('ry', 3)
      .attr('x', (d) => d3.timeWeek.count(start, d) * (cell + gap))
      .attr('y', (d) => d.getDay() * (cell + gap) + 18)
      .attr('fill', (d) => {
        const key = d.toISOString().slice(0, 10);
        const item = byDate.get(key);
        return item ? colors[item.mood] : colors[0];
      })
      .attr('data-date', (d) => d.toISOString().slice(0, 10))
      .attr('data-mood', (d) => {
        const key = d.toISOString().slice(0, 10);
        const item = byDate.get(key);
        return item ? item.mood : 0;
      })
      .style('animation-delay', (d, i) => `${i * 2.5}ms`);

    // --- Hover Tooltips ---
    cells.on('mouseover', function (event, d) {
      const key = d.toISOString().slice(0, 10);
      const item = byDate.get(key);
      
      let htmlContent = '';
      const formattedDate = d.toLocaleDateString('en-US', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        timeZone: 'UTC'
      });
      
      if (item) {
        const riskClass = item.risk.toLowerCase();
        htmlContent = `
          <strong>${formattedDate}</strong>
          <div>Mood: ${moodLabels[item.mood]}</div>
          <div class="mt-1"><span class="badge risk-bg-${riskClass}">${item.risk} Risk</span></div>
        `;
      } else {
        htmlContent = `
          <strong>${formattedDate}</strong>
          <span style="color: var(--dt-muted);">No entries logged</span>
        `;
      }
      
      if (tooltip) {
        tooltip.innerHTML = htmlContent;
        tooltip.style.display = 'block';
        if (window.lucide) window.lucide.createIcons({ node: tooltip });
      }
    })
    .on('mousemove', function (event) {
      if (tooltip) {
        tooltip.style.left = (event.clientX + 14) + 'px';
        tooltip.style.top = (event.clientY - 12) + 'px';
      }
    })
    .on('mouseout', function () {
      if (tooltip) tooltip.style.display = 'none';
    });

    // --- Click to View details / Log day ---
    cells.on('click', function (event, d) {
      cells.classed('selected', false);
      d3.select(this).classed('selected', true);
      
      const key = d.toISOString().slice(0, 10);
      const item = byDate.get(key);
      
      selectedCellData = { date: key, item: item };
      showDetails(key, item);
    });

    // Restore selection highlight if rendered for same year
    if (selectedCellData && new Date(selectedCellData.date).getFullYear() === year) {
      cells.each(function(d) {
        const key = d.toISOString().slice(0, 10);
        if (key === selectedCellData.date) {
          d3.select(this).classed('selected', true);
        }
      });
    }

    svg.selectAll('text.month')
      .data(d3.timeMonths(start, end))
      .join('text')
      .attr('class', 'month')
      .attr('x', (d) => d3.timeWeek.count(start, d) * (cell + gap))
      .attr('y', 10)
      .attr('font-size', 10)
      .attr('fill', 'currentColor')
      .text((d) => d.toLocaleString('en', { month: 'short' }));
  }

  // --- Show Detail Card content ---
  function showDetails(dateStr, item) {
    if (!detailCard || !detailDefault || !detailContent) return;
    
    detailDefault.classList.add('d-none');
    detailContent.classList.remove('d-none');
    
    const d = new Date(dateStr);
    const formattedDate = d.toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      timeZone: 'UTC'
    });

    if (item) {
      const id = item.id;
      const editLogUrl = id ? `/log/${id}/edit` : `/log?date=${dateStr}`;
      const riskClass = item.risk.toLowerCase();
      
      detailContent.innerHTML = `
        <div class="d-flex justify-content-between align-items-start mb-3 border-bottom pb-2 flex-wrap gap-2">
          <div>
            <h4 class="text-slate-900 dark:text-white font-extrabold text-base mb-1">${formattedDate}</h4>
            <span class="badge risk-bg-${riskClass}">${item.risk} Burnout Risk</span>
          </div>
          <a class="daytone-btn-primary daytone-btn-sm inline-flex items-center gap-1.5 text-xs font-bold px-3.5 py-1.5 rounded-full text-decoration-none shadow-sm" href="${editLogUrl}">
            <i data-lucide="pencil" style="width: 13px; height: 13px;"></i>Edit check-in
          </a>
        </div>
        <div class="row g-3">
          <div class="col-6">
            <span class="text-slate-600 dark:text-slate-400 text-xs font-semibold block mb-0.5">Mood score</span>
            <span class="text-slate-900 dark:text-white font-extrabold text-sm">${moodLabels[item.mood]}</span>
          </div>
          <div class="col-6">
            <span class="text-slate-600 dark:text-slate-400 text-xs font-semibold block mb-0.5">Log status</span>
            <span class="text-emerald-700 dark:text-emerald-400 text-xs font-bold inline-flex items-center gap-1"><i data-lucide="check" style="width: 14px; height: 14px;"></i> Logged</span>
          </div>
        </div>
        <p class="text-slate-600 dark:text-slate-400 text-xs font-medium mt-3 mb-0">Check your History tab for notes and model confidence details for this entry.</p>
      `;
    } else {
      const logUrl = `/log?date=${dateStr}`;
      detailContent.innerHTML = `
        <div class="d-flex justify-content-between align-items-start mb-3 border-bottom pb-2 flex-wrap gap-2">
          <div>
            <h4 class="text-slate-900 dark:text-white font-extrabold text-base mb-1">${formattedDate}</h4>
            <span class="text-slate-600 dark:text-slate-400 text-xs font-semibold">No check-in recorded</span>
          </div>
          <a class="daytone-btn-primary daytone-btn-sm inline-flex items-center gap-1.5 text-xs font-bold px-3.5 py-1.5 rounded-full text-decoration-none shadow-sm" href="${logUrl}">
            <i data-lucide="plus" style="width: 13px; height: 13px;"></i>Log this day
          </a>
        </div>
        <p class="text-slate-600 dark:text-slate-400 text-xs font-medium mb-0">You haven't logged your wellness metrics for this day. Click the button above to log retrospectively!</p>
      `;
    }
    
    if (window.lucide) window.lucide.createIcons({ node: detailContent });
  }

  // --- Legend Hover Filter Highlight ---
  legendItems.forEach(item => {
    item.addEventListener('mouseenter', () => {
      const val = item.dataset.moodVal;
      d3.selectAll('.heat-cell').classed('dimmed', function() {
        return d3.select(this).attr('data-mood') !== val;
      });
    });
    
    item.addEventListener('mouseleave', () => {
      d3.selectAll('.heat-cell').classed('dimmed', false);
    });
  });

  // --- Initialize Year Selector ---
  function initYearSelector() {
    if (!yearSelector) return;
    yearSelector.innerHTML = `
      <button type="button" class="range-btn active" data-year="${selectedYear}">${selectedYear}</button>
      <button type="button" class="range-btn" data-year="${selectedYear - 1}">${selectedYear - 1}</button>
    `;
    
    const yearButtons = yearSelector.querySelectorAll('.range-btn');
    yearButtons.forEach(btn => {
      btn.addEventListener('click', async () => {
        yearButtons.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        
        selectedYear = parseInt(btn.dataset.year, 10);
        await loadData(selectedYear);
        renderHeatmap(selectedYear);
      });
    });
  }

  // Initial render
  (async function init() {
    initYearSelector();
    await loadData(selectedYear);
    renderHeatmap(selectedYear);
  })();

  window.addEventListener('daytone-theme-changed', () => {
    renderHeatmap(selectedYear);
  });
})();
