// 给所有笔记添加主题切换按钮 + 主题脚本
// 用法：node scripts/add-theme-toggle.js

const fs = require('fs');
const path = require('path');

const notesDir = path.join(__dirname, '..', 'notes');
const themeToggle = `
<button id="theme-toggle" onclick="toggleTheme()" aria-label="切换主题">🌙</button>
<script>
(function(){
  var t=localStorage.getItem('theme')||'dark';
  if(t==='light')document.documentElement.setAttribute('data-theme','light');
  function upd(){var btn=document.getElementById('theme-toggle');if(btn)btn.textContent=t==='light'?'☀️':'🌙';}
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',upd);else upd();
})();
function toggleTheme(){
  var r=document.documentElement,cur=r.getAttribute('data-theme')==='light'?'light':'dark';
  var nxt=cur==='light'?'dark':'light';
  nxt==='light'?r.setAttribute('data-theme','light'):r.removeAttribute('data-theme');
  localStorage.setItem('theme',nxt);
  document.getElementById('theme-toggle').textContent=nxt==='light'?'☀️':'🌙';
}
</script>`;

let count = 0;
const files = fs.readdirSync(notesDir).filter(f => f.endsWith('.html'));

files.forEach(file => {
  const filePath = path.join(notesDir, file);
  let html = fs.readFileSync(filePath, 'utf8');
  
  // 跳过已有主题切换的
  if (html.includes('theme-toggle')) { count++; return; }
  
  // 在 </body> 前插入主题切换按钮和脚本
  if (html.includes('</body>')) {
    html = html.replace('</body>', themeToggle + '\n</body>');
    fs.writeFileSync(filePath, html, 'utf8');
    count++;
  }
});

console.log(`✅ 已为 ${count}/${files.length} 篇笔记添加主题切换`);
