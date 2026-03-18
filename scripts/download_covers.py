#!/usr/bin/env python3
"""并发批量下载封面 - 修复版"""
import json, os, re, time, urllib.request, concurrent.futures, threading

BOOKLIST_DIR = "/home/gem/workspace/agent/workspace/my-booklist"
DATA_FILE = os.path.join(BOOKLIST_DIR, "js/data.js")
COVERS_DIR = os.path.join(BOOKLIST_DIR, "img/covers")
os.makedirs(COVERS_DIR, exist_ok=True)

stats = {"ok": 0, "fail": 0, "skip": 0}
lock = threading.Lock()

def load_data():
    with open(DATA_FILE) as f:
        content = f.read()
    eq = content.index('=')
    semi = content.rindex(';')
    return json.loads(content[eq+1:semi].strip()), content

def save_data(data, original):
    with open(DATA_FILE) as f:
        content = f.read()
    eq = content.index('=')
    semi = content.rindex(';')
    new_content = content[:eq+1] + '\n' + json.dumps(data, ensure_ascii=False, indent=2) + content[semi:]
    with open(DATA_FILE, 'w') as f:
        f.write(new_content)

def download_cover(isbn):
    isbn = isbn.replace('-', '')
    # Open Library - 6s timeout
    url = f"https://covers.openlibrary.org/b/isbn/{isbn}-L.jpg"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        resp = urllib.request.urlopen(req, timeout=6)
        data = resp.read()
        if len(data) > 2000: return True, data
    except: pass
    # Douban
    try:
        url2 = f"https://book.douban.com/subject_search?search_text={isbn}&cat=1001"
        req = urllib.request.Request(url2, headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Referer": "https://book.douban.com/"})
        resp = urllib.request.urlopen(req, timeout=10)
        html = resp.read().decode('utf-8', errors='ignore')
        covers = re.findall(r'https://img\d+\.doubanio\.com/view/subject/l/public/s\d+\.(?:jpg|png|webp)', html)
        if covers:
            req2 = urllib.request.Request(covers[0], headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
                "Referer": "https://book.douban.com/"})
            resp2 = urllib.request.urlopen(req2, timeout=10)
            data = resp2.read()
            if len(data) > 2000: return True, data
    except: pass
    return False, None

def process_book(item):
    i, isbn, title = item
    filename = f"{isbn}.jpg"
    filepath = os.path.join(COVERS_DIR, filename)
    if os.path.exists(filepath) and os.path.getsize(filepath) > 2000:
        with lock: stats["skip"] += 1
        return i, f"img/covers/{filename}", True
    ok, data = download_cover(isbn)
    if ok:
        with open(filepath, 'wb') as f: f.write(data)
        with lock: stats["ok"] += 1
        return i, f"img/covers/{filename}", True
    with lock: stats["fail"] += 1
    return i, None, False

def main():
    data, orig = load_data()
    books = data['BOOKS']
    
    need = []
    for i, b in enumerate(books):
        isbn = b.get('isbn', '').replace('-', '')
        cover = b.get('cover', '')
        if isbn and ('openlibrary' in cover or not cover or not cover.startswith('img/')):
            need.append((i, isbn, b['title']))
    
    print(f"总书籍: {len(books)} | 需下载: {len(need)} | 跳过: {stats['skip']}")
    print(f"并发: 10线程 | 超时: OpenLib 6s / Douban 10s")
    print("=" * 60)
    
    done = 0
    start = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as ex:
        futures = {ex.submit(process_book, item): item for item in need}
        for f in concurrent.futures.as_completed(futures):
            idx, path, ok = f.result()
            done += 1
            title = books[idx]['title'][:30]
            if ok:
                books[idx]['cover'] = path
                print(f"[{done}/{len(need)}] ✅ {title}", flush=True)
            else:
                print(f"[{done}/{len(need)}] ❌ {title}", flush=True)
            
            if done % 50 == 0:
                save_data(data, orig)
                elapsed = time.time() - start
                print(f"  💾 已保存 | {done}/{len(need)} | {elapsed/60:.1f}min", flush=True)
    
    save_data(data, orig)
    elapsed = time.time() - start
    print(f"\n{'='*60}")
    print(f"✅ 成功: {stats['ok']} | ❌ 失败: {stats['fail']} | ⏭ 跳过: {stats['skip']}")
    print(f"⏱ 耗时: {elapsed/60:.1f}分钟")

if __name__ == "__main__":
    main()
