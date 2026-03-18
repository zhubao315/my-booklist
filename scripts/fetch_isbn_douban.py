#!/usr/bin/env python3
"""从豆瓣搜索获取 ISBN（低频请求，避免被封）"""
import json, os, re, time, random, urllib.request, urllib.parse

BOOKLIST_DIR = "/home/gem/workspace/agent/workspace/my-booklist"
DATA_FILE = os.path.join(BOOKLIST_DIR, "js/data.js")

def load_data():
    with open(DATA_FILE) as f:
        content = f.read()
    eq = content.index('=')
    semi = content.rindex(';')
    return json.loads(content[eq+1:semi].strip()), content

def save_data(data):
    with open(DATA_FILE) as f:
        content = f.read()
    eq = content.index('=')
    semi = content.rindex(';')
    new_content = content[:eq+1] + '\n' + json.dumps(data, ensure_ascii=False, indent=2) + content[semi:]
    with open(DATA_FILE, 'w') as f:
        f.write(new_content)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Referer": "https://book.douban.com/",
}

def search_douban(title, author):
    """Search Douban for a book and return subject URL"""
    # Clean title (remove《》)
    clean_title = re.sub(r'[《》]', '', title).strip()
    # Clean author (take first author, remove translators)
    clean_author = re.sub(r'[，,、].*', '', author).strip()
    
    query = clean_title + " " + clean_author
    query = query[:50]  # limit length
    
    encoded = urllib.parse.quote(query)
    url = f"https://book.douban.com/subject_search?search_text={encoded}&cat=1001"
    
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        resp = urllib.request.urlopen(req, timeout=15)
        html = resp.read().decode('utf-8', errors='ignore')
        
        # Find subject URLs: /subject/12345678/
        subjects = re.findall(r'/subject/(\d+)/', html)
        if subjects:
            # Return the first unique subject id
            seen = set()
            for s in subjects:
                if s not in seen:
                    seen.add(s)
                    return s
    except Exception as e:
        print(f"  ⚠ 搜索失败: {e}")
    return None

def get_isbn_from_subject(subject_id):
    """Get ISBN from Douban subject page"""
    url = f"https://book.douban.com/subject/{subject_id}/"
    
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        resp = urllib.request.urlopen(req, timeout=15)
        html = resp.read().decode('utf-8', errors='ignore')
        
        # Pattern: <span class="pl">ISBN:</span> followed by the number
        isbn = re.search(r'<span class="pl">ISBN:</span>\s*(\d+)', html)
        if isbn:
            return isbn.group(1)
        
        # Fallback
        isbn2 = re.search(r'ISBN[：:]\s*(\d[\d\-]{9,16})', html)
        if isbn2:
            return isbn2.group(1).replace('-', '')
            
    except Exception as e:
        print(f"  ⚠ 详情页失败: {e}")
    return None

def main():
    data, _ = load_data()
    books = data['BOOKS']
    
    no_isbn = [(i, b) for i, b in enumerate(books) if not b.get('isbn')]
    
    print(f"总书籍: {len(books)} | 需获取 ISBN: {len(no_isbn)}")
    print(f"请求间隔: 3-5 秒（避免被封）")
    print("=" * 60)
    
    ok, fail = 0, 0
    start = time.time()
    
    for count, (i, book) in enumerate(no_isbn, 1):
        title = book['title'][:30]
        print(f"[{count}/{len(no_isbn)}] 🔍 {title}", end="", flush=True)
        
        subject_id = search_douban(book['title'], book.get('author', ''))
        
        if subject_id:
            # Wait between search and detail page
            time.sleep(random.uniform(1.5, 3))
            
            isbn = get_isbn_from_subject(subject_id)
            if isbn:
                books[i]['isbn'] = isbn
                print(f" → ✅ ISBN: {isbn}")
                ok += 1
            else:
                print(f" → ❌ 找不到 ISBN")
                fail += 1
        else:
            print(f" → ❌ 未找到")
            fail += 1
        
        # Save every 20 books
        if count % 20 == 0:
            save_data(data)
            print(f"  💾 已保存进度 ({count}/{len(no_isbn)})")
        
        # Random delay between requests
        if count < len(no_isbn):
            delay = random.uniform(3, 5)
            time.sleep(delay)
    
    save_data(data)
    elapsed = time.time() - start
    print(f"\n{'='*60}")
    print(f"✅ 成功: {ok} | ❌ 失败: {fail} | ⏱ {elapsed/60:.1f}分钟")

if __name__ == "__main__":
    main()
