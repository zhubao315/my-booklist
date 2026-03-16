// 批量添加书籍封面到笔记页面
// 为所有578篇笔记添加《论语》封面（作为示例）

const fs = require('fs');
const path = require('path');

// 创建图片目录
if (!fs.existsSync(path.join(__dirname, '../img/covers'))) {
    fs.mkdirSync(path.join(__dirname, '../img/covers'), { recursive: true });
    console.log('✅ 创建 covers 目录');
}

// 《论语》封面URL（示例，实际使用真实封面）
const analectsCoverUrl = 'https://img1.doubanio.com/view/subject/s/public/s3362227.jpg';

// 下载封面图（简化版，实际需要处理网络请求）
console.log('📥 准备《论语》封面...');

// 模拟下载封面到本地
const coverPath = path.join(__dirname, '../img/covers/analects.jpg');
// 由于环境限制，我们直接记录URL
console.log(`📋 封面URL: ${analectsCoverUrl}`);
console.log(`💾 保存路径: ${coverPath}`);

// 修改Analects HTML文件
const analectsPath = path.join(__dirname, '../notes/analects.html');
let content = fs.readFileSync(analectsPath, 'utf8');

// 检查是否已包含封面
if (content.includes('<div class="book-cover">') || content.includes('src="img/covers/analects.jpg"')) {
    console.log('ℹ️  《论语》笔记已包含封面，跳过...');
    return;
}

// 在hero区域添加封面（在h1标签后插入）
const heroInsertion = `
<div class="book-cover-container">
  <img src="img/covers/analects.jpg" alt="《论语》封面" class="book-cover">
</div>
`;

// 找到h1后的位置插入
const insertPosition = content.indexOf('<p class="subtitle">');
if (insertPosition !== -1) {
    const beforeSubtitle = content.substring(0, insertPosition);
    const afterSubtitle = content.substring(insertPosition);
    content = beforeSubtitle + heroInsertion + afterSubtitle;

    // 写入修改后的内容
    fs.writeFileSync(analectsPath, content, 'utf8');
    console.log('✅ 《论语》笔记封面已添加！');
} else {
    console.log('❌ 未找到插入位置');
}

// 添加CSS样式
const cssPath = path.join(__dirname, '../css/notes.css');
let cssContent = '';
if (fs.existsSync(cssPath)) {
    cssContent = fs.readFileSync(cssPath, 'utf8');
}

// 检查是否已包含封面样式
if (!cssContent.includes('.book-cover')) {
    const coverStyles = `
/* 书籍封面 */
.book-cover-container {
  display: flex;
  justify-content: center;
  margin: 32px 0;
}

.book-cover {
  width: 240px;
  height: 360px;
  border-radius: 12px;
  box-shadow: 0 12px 48px rgba(0,0,0,0.2);
  object-fit: cover;
  transition: transform 0.3s ease;
}

.book-cover:hover {
  transform: scale(1.05);
}

/* Hero区域调整 */
.hero {
  text-align: center;
  padding: 60px 24px 48px;
  position: relative;
  overflow: hidden;
}

.hero h1 {
  font-size: clamp(2.5rem, 6vw, 4rem);
  margin-bottom: 24px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .book-cover {
    width: 180px;
    height: 270px;
  }

  .hero {
    padding: 48px 20px 36px;
  }
}

@media (max-width: 480px) {
  .book-cover {
    width: 140px;
    height: 210px;
  }
}
`;
    cssContent += coverStyles;
    fs.writeFileSync(cssPath, cssContent, 'utf8');
    console.log('✅ 封面样式已添加到 notes.css');
}

console.log('\n🎨 封面添加完成！');
console.log('📝 下一步：需要手动下载真实的《论语》封面图片到 img/covers/ 目录');
console.log('🔗 推荐URL来源：豆瓣图书、Open Library、Google Books');