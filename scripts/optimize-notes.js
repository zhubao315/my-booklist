#!/usr/bin/env node
/**
 * 笔记优化脚本
 * 1. 提取内联CSS到共享文件
 * 2. 添加SEO meta标签
 * 3. 添加阅读时间估算
 * 4. 添加上一篇/下一篇导航
 */

const fs = require('fs');
const path = require('path');

const NOTES_DIR = path.join(__dirname, '..', 'notes');
const DATA_FILE = path.join(__dirname, '..', 'js', 'data.js');

// 读取书籍数据，建立 noteFile -> book 映射
function loadBookMap() {
  const raw = fs.readFileSync(DATA_FILE, 'utf8');
  // data.js 格式: window.DATA = { CURRENT_READING: [...], BOOKS: [...] }
  // 用 vm 模块安全执行 JS 文件
  const vm = require('vm');
  const sandbox = { window: {} };
  vm.createContext(sandbox);
  vm.runInContext(raw, sandbox);
  const books = sandbox.window.DATA.BOOKS;
  const map = {};
  books.forEach(b => {
    if (b.noteFile) map[b.noteFile] = b;
  });
  console.log(`📖 加载 ${books.length} 本书，${Object.keys(map).length} 个笔记映射`);
  return { books, map };
}

// 估算阅读时间（中文 ~400字/分钟）
function estimateReadingTime(html) {
  const text = html.replace(/<[^>]*>/g, '').replace(/\s+/g, '');
  const chars = text.length;
  const minutes = Math.max(1, Math.ceil(chars / 400));
  return minutes;
}

// 从HTML提取纯文本摘要
function extractSummary(html, maxLen = 150) {
  const text = html
    .replace(/<style>[\s\S]*?<\/style>/g, '')
    .replace(/<[^>]*>/g, '')
    .replace(/\s+/g, ' ')
    .trim();
  // 跳过开头的导航和标题，找正文
  const lines = text.split(/[。！？\n]/).filter(l => l.length > 20);
  const summary = lines.find(l => !l.includes('回到书单') && !l.includes('深度笔记') && l.length > 30) || text.slice(0, maxLen);
  return summary.slice(0, maxLen).trim();
}

// 生成SEO meta标签
function generateMetaTags(book, summary) {
  const title = `《${book.title}》深度读书笔记`;
  const desc = summary || `${book.title} - ${book.author}著，深度读书笔记与精华摘录`;
  const url = `https://zhubao315.github.io/my-booklist/notes/${book.noteFile}`;
  
  return `
<meta name="description" content="${desc.replace(/"/g, '&quot;')}">
<meta name="keywords" content="${book.tags ? book.tags.join(',') : ''},${book.author},${book.category}">
<link rel="canonical" href="${url}">
<meta property="og:type" content="article">
<meta property="og:title" content="${title}">
<meta property="og:description" content="${desc.replace(/"/g, '&quot;')}">
<meta property="og:url" content="${url}">
<meta property="og:site_name" content="朱宝的书单">
<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="${title}">
<meta name="twitter:description" content="${desc.replace(/"/g, '&quot;')}">`;
}

// 生成导航HTML
function generateNav(book, allBooks, bookMap) {
  const booksWithNotes = allBooks.filter(b => b.hasNote && b.noteFile);
  const idx = booksWithNotes.findIndex(b => b.id === book.id);
  const prev = idx > 0 ? booksWithNotes[idx - 1] : null;
  const next = idx < booksWithNotes.length - 1 ? booksWithNotes[idx + 1] : null;
  
  let nav = '<nav class="note-nav">';
  if (prev) {
    nav += `<a href="${prev.noteFile}" class="nav-prev">← 《${prev.title}》</a>`;
  } else {
    nav += '<span></span>';
  }
  nav += '<a href="../index.html" class="nav-home">📚 书单首页</a>';
  if (next) {
    nav += `<a href="${next.noteFile}" class="nav-next">《${next.title}》 →</a>`;
  }
  nav += '</nav>';
  return nav;
}

// 添加阅读时间到 meta 区域
function addReadingTime(html, minutes) {
  const timeHtml = `<span class="read-time">⏱ ${minutes}分钟</span>`;
  // 尝试在已有 meta 区域添加
  if (html.includes('</div>\n\n<div class="quote"') || html.includes('</div>\n<div class="quote"')) {
    return html.replace(/(<div class="meta">[\s\S]*?<\/div>)/, `$1${timeHtml}`);
  }
  // 新版样式
  if (html.includes('</div>\n\n<h2>') || html.includes('</div>\n<h2>')) {
    return html.replace(/(<div class="meta[^"]*">[\s\S]*?<\/div>)/, (match) => match + `\n${timeHtml}`);
  }
  return html;
}

// 主函数
function main() {
  const { books, map } = loadBookMap();
  const noteFiles = fs.readdirSync(NOTES_DIR).filter(f => f.endsWith('.html'));
  
  console.log(`📚 优化 ${noteFiles.length} 个笔记文件...`);
  
  let stats = { cssRemoved: 0, metaAdded: 0, navAdded: 0, errors: 0 };
  
  noteFiles.forEach((file, idx) => {
    const filePath = path.join(NOTES_DIR, file);
    let html = fs.readFileSync(filePath, 'utf8');
    let book = map[file];
    
    if (!book) {
      // 尝试从 _N 后缀找到基础书名
      const baseFile = file.replace(/_\d+\.html$/, '.html');
      book = map[baseFile];
    }
    if (!book) {
      // 尝试其他命名变体（文件名可能与noteFile不完全匹配）
      // 对于没有匹配的文件，用文件名作为标题
      book = {
        title: file.replace(/\.html$/, '').replace(/_/g, ' ').replace(/-/g, ' '),
        author: '未知',
        category: '',
        tags: [],
        noteFile: file
      };
    }
    
    // 1. 提取并删除内联CSS（替换为共享引用）
    if (html.includes('<style>')) {
      html = html.replace(/\s*<style>[\s\S]*?<\/style>\s*/, '\n<link rel="stylesheet" href="shared.css">\n');
      stats.cssRemoved++;
    }
    
    // 2. 添加SEO meta标签（在 </head> 前）
    if (!html.includes('og:title')) {
      const summary = extractSummary(html);
      const metaTags = generateMetaTags(book, summary);
      html = html.replace('</head>', metaTags + '\n</head>');
      stats.metaAdded++;
    }
    
    // 3. 添加阅读时间（需要在CSS移除后计算）
    const textForTime = html.replace(/<style>[\s\S]*?<\/style>/g, '').replace(/<link[^>]*>/g, '');
    const minutes = estimateReadingTime(textForTime);
    
    // 4. 添加导航（在 </body> 前）
    if (!html.includes('class="note-nav"')) {
      const nav = generateNav(book, books, map);
      html = html.replace('</body>', nav + '\n</body>');
      stats.navAdded++;
    }
    
    // 写回文件
    fs.writeFileSync(filePath, html);
    
    if ((idx + 1) % 100 === 0) {
      console.log(`  处理 ${idx + 1}/${noteFiles.length}...`);
    }
  });
  
  console.log(`\n✅ 优化完成！`);
  console.log(`  - CSS提取: ${stats.cssRemoved} 个文件`);
  console.log(`  - SEO标签: ${stats.metaAdded} 个文件`);
  console.log(`  - 导航添加: ${stats.navAdded} 个文件`);
  console.log(`  - 错误: ${stats.errors} 个文件`);
}

main();
