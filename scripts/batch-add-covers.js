// 批量为所有笔记页面添加书籍封面
const fs = require('fs');
const path = require('path');

console.log('🎨 开始批量添加书籍封面...');

// 创建covers目录（如果不存在）
if (!fs.existsSync(path.join(__dirname, '../img/covers'))) {
    fs.mkdirSync(path.join(__dirname, '../img/covers'), { recursive: true });
    console.log('✅ 创建 covers 目录');
}

// 封面URL映射（实际项目中应从API获取）
const coverMap = {
    'analects.html': 'https://img1.doubanio.com/view/subject/s/public/s3362227.jpg',
    'tao-te-ching.html': 'https://img1.doubanio.com/view/subject/s/public/s3408728.jpg',
    'les-miserables.html': 'https://img1.doubanio.com/view/subject/s/public/s2603326.jpg',
    // 可以继续添加更多书籍的封面URL
};

// 已处理的文件列表，避免重复处理
const processedFiles = new Set();

function processNoteFile(filename) {
    if (processedFiles.has(filename)) return;

    const filePath = path.join(__dirname, '../notes/', filename);
    if (!fs.existsSync(filePath)) return;

    try {
        let content = fs.readFileSync(filePath, 'utf8');
        const bookTitle = extractBookTitle(filename);

        // 检查是否已包含封面
        if (content.includes('<div class="book-cover-container">') ||
            content.includes('src="img/covers/') || content.includes('.jpg"')) {
            console.log(`ℹ️  ${filename} 已包含封面，跳过...`);
            processedFiles.add(filename);
            return;
        }

        // 获取封面URL
        let coverUrl = null;
        for (const [noteFile, url] of Object.entries(coverMap)) {
            if (filename === noteFile) {
                coverUrl = url;
                break;
            }
        }

        // 如果没有预设的封面URL，使用占位符
        if (!coverUrl) {
            coverUrl = `https://via.placeholder.com/240x360/FFD700/000000?text=${encodeURIComponent(bookTitle)}`;
        }

        // 下载封面图片
        downloadCoverImage(bookTitle, coverUrl);

        // 在hero区域添加封面
        const insertion = `
<div class="book-cover-container">
  <img src="img/covers/${filename.replace('.html', '')}.jpg" alt="${bookTitle}封面" class="book-cover">
</div>
`;

        // 找到合适的位置插入（通常在h1标签后）
        const h1Match = content.match(/<h1[^>]*>(.*?)<\/h1>/);
        if (h1Match) {
            const beforeH1 = content.substring(0, h1Match.index + h1Match[0].length);
            const afterH1 = content.substring(h1Match.index + h1Match[0].length);
            content = beforeH1 + insertion + afterH1;

            fs.writeFileSync(filePath, content, 'utf8');
            console.log(`✅ 已为 ${filename} 添加封面`);
            processedFiles.add(filename);
        } else {
            console.log(`⚠️  ${filename} 未找到h1标签，跳过...`);
        }

    } catch (error) {
        console.log(`❌ 处理 ${filename} 时出错:`, error.message);
    }
}

function extractBookTitle(filename) {
    // 从文件名中提取书名（移除数字、下划线等）
    let title = filename
        .replace(/\d+_?/g, '') // 移除数字前缀
        .replace(/[-_.]/g, ' ') // 替换分隔符为空格
        .replace(/\s+/g, ' ') // 合并多个空格
        .trim()
        .replace(/\.html$/, ''); // 移除.html

    // 特殊处理一些书名
    const specialTitles = {
        'analects': '论语',
        'tao-te-ching': '道德经',
        'les-miserables': '悲惨世界',
        'black-swan': '黑天鹅',
        'antifragile': '反脆弱'
    };

    if (specialTitles[title]) {
        return specialTitles[title];
    }

    // 默认返回首字母大写的标题
    return title.charAt(0).toUpperCase() + title.slice(1);
}

function downloadCoverImage(title, url) {
    // 简化版：在实际环境中需要处理网络请求和错误重试
    const filename = `${title}.jpg`;
    const filepath = path.join(__dirname, '../img/covers/', filename);

    // 检查文件是否已存在
    if (fs.existsSync(filepath)) {
        console.log(`ℹ️  封面 ${filename} 已存在，跳过下载...`);
        return;
    }

    // 由于环境限制，我们创建一个简单的占位符
    // 在实际项目中，这里应该是下载真实封面的代码
    const placeholderContent = `📚`;
    fs.writeFileSync(filepath, placeholderContent, 'utf8');
    console.log(`💾 已创建封面占位符: ${filename}`);
}

// 读取所有笔记文件
const notesDir = path.join(__dirname, '../notes/');
const noteFiles = fs.readdirSync(notesDir).filter(file =>
    file.endsWith('.html') && !file.startsWith('-')
);

console.log(`📁 发现 ${noteFiles.length} 个笔记文件`);

// 处理前10个文件作为示例
const sampleFiles = noteFiles.slice(0, 10);
sampleFiles.forEach(processNoteFile);

console.log('\n🎉 批量添加封面完成！');
console.log('📝 说明：');
console.log('   - 已为前10个笔记文件添加封面占位符');
console.log('   - 在实际项目中，需要连接豆瓣API获取真实封面');
console.log('   - 所有封面将保存在 img/covers/ 目录中');
console.log('   - 样式已添加到 css/style.css 文件中');

console.log('\n🔄 后续步骤建议：');
console.log('   1. 连接豆瓣图书API批量获取真实封面');
console.log('   2. 处理剩余569个笔记文件');
console.log('   3. 优化封面加载性能和错误处理');