(function () {
  const root = document.documentElement;
  const saved = localStorage.getItem('daytone-theme');
  let theme = 'light';
  if (saved === 'dark' || saved === 'light') {
    theme = saved;
  } else {
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    theme = prefersDark ? 'dark' : 'light';
  }
  root.setAttribute('data-theme', theme);

  const button = document.getElementById('darkToggle');
  if (!button) return;

  button.addEventListener('click', () => {
    const next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    root.setAttribute('data-theme', next);
    localStorage.setItem('daytone-theme', next);
  });
})();
