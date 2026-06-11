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

  const colors = ['#e5e7eb', '#fee2e2', '#fed7aa', '#fef3c7', '#bbf7d0', '#86efac'];
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
            <h4 style="font-size: 1.15rem; font-weight: 800; color: var(--dt-text); margin-bottom: 0.15rem;">${formattedDate}</h4>
            <span class="badge risk-bg-${riskClass}">${item.risk} Burnout Risk</span>
          </div>
          <a class="btn btn-sm btn-primary d-inline-flex align-items-center gap-1" href="${editLogUrl}">
            <i data-lucide="pencil" style="width: 14px; height: 14px;"></i>Edit check-in
          </a>
        </div>
        <div class="row g-3">
          <div class="col-6">
            <span class="text-secondary small d-block">Mood score</span>
            <span style="font-size: 1.05rem; font-weight: 800; color: var(--dt-text);">${moodLabels[item.mood]}</span>
          </div>
          <div class="col-6">
            <span class="text-secondary small d-block">Log status</span>
            <span class="text-success small fw-bold"><i data-lucide="check" style="width: 14px; height: 14px; vertical-align: middle;"></i> Logged</span>
          </div>
        </div>
        <p class="text-secondary small mt-3 mb-0">Check your History tab for notes and model confidence details for this entry.</p>
      `;
    } else {
      const logUrl = `/log?date=${dateStr}`;
      detailContent.innerHTML = `
        <div class="d-flex justify-content-between align-items-start mb-3 border-bottom pb-2 flex-wrap gap-2">
          <div>
            <h4 style="font-size: 1.15rem; font-weight: 800; color: var(--dt-text); margin-bottom: 0.15rem;">${formattedDate}</h4>
            <span class="text-secondary small">No check-in recorded</span>
          </div>
          <a class="btn btn-sm btn-primary d-inline-flex align-items-center gap-1" href="${logUrl}">
            <i data-lucide="plus" style="width: 14px; height: 14px;"></i>Log this day
          </a>
        </div>
        <p class="text-secondary small mb-0">You haven't logged your wellness metrics for this day. Click the button above to log retrospectively!</p>
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
})();
