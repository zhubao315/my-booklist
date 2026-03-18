// 朱宝的书单 - 笔记页面共享脚本
// localStorage key 与首页保持一致
(function() {
  const KEY = 'theme';
  const btn = document.getElementById('theme-toggle');

  // Load saved theme (默认 dark)
  function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem(KEY, theme);
    if (btn) btn.textContent = theme === 'dark' ? '\u2600\uFE0F' : '\uD83C\uDF19';
    if (btn) btn.title = theme === 'dark' ? '切换到日间模式' : '切换到夜间模式';
  }

  const saved = localStorage.getItem(KEY) || (window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark');
  applyTheme(saved);

  // Toggle
  if (btn) {
    btn.addEventListener('click', function() {
      const current = document.documentElement.getAttribute('data-theme') || 'dark';
      applyTheme(current === 'dark' ? 'light' : 'dark');
    });
  }
})();
