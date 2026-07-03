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

  function updateIcon(themeName) {
    const currentIcon = button.querySelector('i') || button.querySelector('svg');
    if (currentIcon) {
      const newIcon = document.createElement('i');
      newIcon.setAttribute('data-lucide', themeName === 'dark' ? 'sun' : 'moon');
      currentIcon.replaceWith(newIcon);
      if (window.lucide) {
        window.lucide.createIcons({
          node: button
        });
      }
    }
  }

  // Set initial icon on load
  updateIcon(theme);

  button.addEventListener('click', () => {
    const next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    root.setAttribute('data-theme', next);
    localStorage.setItem('daytone-theme', next);
    updateIcon(next);
  });
})();
