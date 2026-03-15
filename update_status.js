const fs = require('fs');
eval(fs.readFileSync('js/data.js', 'utf8'));

var books = window.DATA.BOOKS;
var reading = ['百年孤独','了不起的盖茨比','卓越基因','社会性动物','深度工作','幸福的婚姻','重启人生','掌控习惯','乡土中国','社会分工论','Python机器学习','人生意义'];

var updated = 0;
books.forEach(b => {
  var cleanTitle = b.title.replace(/[《》]/g, '');
  if (!reading.includes(cleanTitle) && b.status !== 'done') {
    b.status = 'done';
    updated++;
  }
});

console.log('Updated:', updated, 'books to done');
console.log('Done:', books.filter(b => b.status === 'done').length);
console.log('Reading:', books.filter(b => b.status === 'reading').length);
console.log('Want:', books.filter(b => b.status === 'want').length);

// Write back
var data = { CATEGORIES: window.DATA.CATEGORIES, BOOKS: books };
var jsonStr = JSON.stringify(data);
jsonStr = jsonStr.replace(/\\/g, '\\\\').replace(/`/g, '\\`').replace(/\$/g, '\\$');
var output = 'window.DATA = eval("(' + jsonStr.replace(/"/g, '\\"') + ')");\n';
fs.writeFileSync('js/data.js', output);
console.log('data.js updated successfully');
