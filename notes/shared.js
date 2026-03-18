// 朱宝的书单 - 笔记页面共享脚本
(function() {
  const KEY = 'booklist-theme';
  const btn = document.getElementById('theme-toggle');
  
  // Load saved theme
  const saved = localStorage.getItem(KEY);
  if (saved === 'light') {
    document.documentElement.setAttribute('data-theme', 'light');
  }
  
  // Update button icon
  function updateBtn() {
    const isLight = document.documentElement.getAttribute('data-theme') === 'light';
    if (btn) btn.textContent = isLight ? '🌙' : '☀️';
    if (btn) btn.title = isLight ? '切换到夜间模式' : '切换到日间模式';
  }
  updateBtn();
  
  // Toggle
  if (btn) {
    btn.addEventListener('click', function() {
      const isLight = document.documentElement.getAttribute('data-theme') === 'light';
      if (isLight) {
        document.documentElement.removeAttribute('data-theme');
        localStorage.setItem(KEY, 'dark');
      } else {
        document.documentElement.setAttribute('data-theme', 'light');
        localStorage.setItem(KEY, 'light');
      }
      updateBtn();
    });
  }
})();
