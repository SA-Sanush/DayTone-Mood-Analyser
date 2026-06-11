(async function () {
  const target = document.getElementById('heatmap');
  if (!target) return;

  let rows = [];
  const now = new Date();
  const year = now.getFullYear();
  try {
    const response = await fetch('/api/heatmap');
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    rows = await response.json();
  } catch (err) {
    console.error("Failed to load heatmap data:", err);
    target.textContent = "Could not load heatmap data. Please try again later.";
    return;
  }

  const byDate = new Map(rows.map((row) => [row.date, row]));
  const start = new Date(year, 0, 1);
  const end = new Date(year, 11, 31);
  const cell = 14;
  const gap = 3;
  const width = 54 * (cell + gap);
  const height = 7 * (cell + gap) + 24;
  const colors = ['#e5e7eb', '#fee2e2', '#fed7aa', '#fef3c7', '#bbf7d0', '#86efac'];

  const svg = d3.select(target).append('svg')
    .attr('viewBox', `0 0 ${width} ${height}`)
    .attr('role', 'img')
    .attr('aria-label', `Mood heatmap for the year ${year}`);
  const days = d3.timeDays(start, d3.timeDay.offset(end, 1));

  svg.selectAll('rect')
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
    .append('title')
    .text((d) => {
      const key = d.toISOString().slice(0, 10);
      const item = byDate.get(key);
      return item ? `${key}: mood ${item.mood}, ${item.risk} risk` : `${key}: no log`;
    });

  svg.selectAll('text.month')
    .data(d3.timeMonths(start, end))
    .join('text')
    .attr('class', 'month')
    .attr('x', (d) => d3.timeWeek.count(start, d) * (cell + gap))
    .attr('y', 10)
    .attr('font-size', 10)
    .attr('fill', 'currentColor')
    .text((d) => d.toLocaleString('en', { month: 'short' }));
})();
