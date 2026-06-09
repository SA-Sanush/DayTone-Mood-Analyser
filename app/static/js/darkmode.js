(function () {
  const root = document.documentElement;
  const saved = localStorage.getItem('daytone-theme') || 'light';
  root.setAttribute('data-theme', saved);

  const button = document.getElementById('darkToggle');
  if (!button) return;

  button.addEventListener('click', () => {
    const next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    root.setAttribute('data-theme', next);
    localStorage.setItem('daytone-theme', next);
  });
})();
