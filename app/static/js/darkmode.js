(function () {
  const root = document.documentElement;
  const saved = localStorage.getItem('daytone-theme');
  let theme = 'light';
  if (saved === 'dark' || saved === 'nocturne' || saved === 'light') {
    theme = (saved === 'dark') ? 'nocturne' : saved;
  } else {
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    theme = prefersDark ? 'nocturne' : 'light';
  }
  const isDarkInitial = theme === 'dark' || theme === 'nocturne';
  root.setAttribute('data-theme', theme);
  root.classList.toggle('dark', isDarkInitial);

  const button = document.getElementById('darkToggle');
  if (!button) return;

  function updateIcon(themeName) {
    const isDark = themeName === 'dark' || themeName === 'nocturne';
    const currentIcon = button.querySelector('i') || button.querySelector('svg');
    if (currentIcon) {
      const newIcon = document.createElement('i');
      newIcon.setAttribute('data-lucide', isDark ? 'sun' : 'moon');
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
    const currentTheme = root.getAttribute('data-theme');
    const wasDark = currentTheme === 'dark' || currentTheme === 'nocturne';
    const next = wasDark ? 'light' : 'nocturne';
    root.setAttribute('data-theme', next);
    root.classList.toggle('dark', !wasDark);
    localStorage.setItem('daytone-theme', next);
    updateIcon(next);
    window.dispatchEvent(new CustomEvent('daytone-theme-changed', { detail: { theme: next } }));
  });
})();
