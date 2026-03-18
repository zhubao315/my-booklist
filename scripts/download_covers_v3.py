#!/usr/bin/env python3
"""封面下载 V3：批量从 OpenLibrary（ISBN）+ Google Books（无ISBN）获取"""
import json, os, re, time, urllib.request, urllib.parse, hashlib, concurrent.futures, threading

BOOKLIST_DIR = "/home/gem/workspace/agent/workspace/my-booklist"
DATA_FILE = os.path.join(BOOKLIST_DIR, "js/data.js")
COVERS_DIR = os.path.join(BOOKLIST_DIR, "img/covers")
os.makedirs(COVERS_DIR, exist_ok=True)

stats = {"ok": 0, "fail": 0, "skip": 0, "google_ok": 0, "google_fail": 0}
lock = threading.Lock()

COLORS = [
    ("#E8A838", "#FFF"), ("#4A6FA5", "#FFF"), ("#E84B4B", "#FFF"),
    ("#2D6A4F", "#FFF"), ("#6B4E8A", "#FFF"), ("#D4A373", "#FFF"),
    ("#2C3E50", "#FFF"), ("#E74C3C", "#FFF"), ("#1ABC9C", "#FFF"),
    ("#9B59B6", "#FFF"), ("#F39C12", "#FFF"), ("#3498DB", "#FFF"),
    ("#E67E22", "#FFF"), ("#16A085", "#FFF"), ("#C0392B", "#FFF"),
]

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

def download_from_openlibrary(isbn):
    url = f"https://covers.openlibrary.org/b/isbn/{isbn}-L.jpg"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        resp = urllib.request.urlopen(req, timeout=10)
        data = resp.read()
        if len(data) > 3000:
            return True, data
    except:
        pass
    return False, None

def download_from_google(title, author):
    query = title + " " + re.sub(r'[，,、].*', '', author).strip()
    query = query[:80]
    encoded = urllib.parse.quote(query)
    url = f"https://www.googleapis.com/books/v1/volumes?q={encoded}&maxResults=1&printType=books"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        resp = urllib.request.urlopen(req, timeout=10)
        data = json.loads(resp.read().decode('utf-8'))
        if data.get('totalItems', 0) > 0:
            images = data['items'][0].get('volumeInfo', {}).get('imageLinks', {})
            for key in ['thumbnail', 'smallThumbnail']:
                if key in images:
                    img_url = images[key].replace('http:', 'https:')
                    req2 = urllib.request.Request(img_url, headers={"User-Agent": "Mozilla/5.0"})
                    resp2 = urllib.request.urlopen(req2, timeout=10)
                    img_data = resp2.read()
                    if len(img_data) > 2000:
                        return True, img_data
    except:
        pass
    return False, None

def generate_placeholder(title, book_id):
    bg, fg = COLORS[book_id % len(COLORS)]
    first = title.strip()[0] if title else '?'
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="200" height="300" viewBox="0 0 200 300"><rect width="200" height="300" fill="{bg}" rx="8"/><text x="100" y="155" text-anchor="middle" fill="{fg}" font-size="48" font-weight="bold" font-family="system-ui">{first}</text></svg>'
    return svg.encode('utf-8')

def process_book(item):
    i, book = item
    isbn = book.get('isbn', '').replace('-', '')
    title = book.get('title', '')
    
    # Determine filename
    if isbn:
        filename = f"{isbn}.jpg"
    else:
        h = hashlib.md5(title.encode()).hexdigest()[:8]
        filename = f"title_{h}.jpg"
    filepath = os.path.join(COVERS_DIR, filename)
    
    # Already exists?
    if os.path.exists(filepath) and os.path.getsize(filepath) > 2000:
        with lock: stats["skip"] += 1
        return i, f"img/covers/{filename}", True
    
    # Try OpenLibrary (ISBN)
    if isbn:
        ok, data = download_from_openlibrary(isbn)
        if ok:
            with open(filepath, 'wb') as f:
                f.write(data)
            with lock: stats["ok"] += 1
            return i, f"img/covers/{filename}", True
    
    # Try Google Books (title + author)
    ok, data = download_from_google(title, book.get('author', ''))
    if ok:
        with open(filepath, 'wb') as f:
            f.write(data)
        with lock: stats["google_ok"] += 1
        return i, f"img/covers/{filename}", True
    
    # Placeholder
    h = hashlib.md5(title.encode()).hexdigest()[:8]
    ph_name = f"placeholder_{h}.svg"
    ph_path = os.path.join(COVERS_DIR, ph_name)
    if not os.path.exists(ph_path):
        with open(ph_path, 'wb') as f:
            f.write(generate_placeholder(title, book['id']))
    with lock: stats["google_fail"] += 1
    return i, f"img/covers/{ph_name}", False

def main():
    data, _ = load_data()
    books = data['BOOKS']
    
    need = []
    for i, b in enumerate(books):
        cover = b.get('cover', '')
        if cover.startswith('img/covers/'):
            fp = os.path.join(BOOKLIST_DIR, cover)
            if os.path.exists(fp) and os.path.getsize(fp) > 2000:
                continue
        elif cover.startswith('http') or not cover:
            pass  # need to re-download
        else:
            continue
        need.append((i, b))
    
    print(f"总书籍: {len(books)} | 已有封面: {len(books)-len(need)} | 需处理: {len(need)}")
    print(f"并发: 15线程")
    print("=" * 60)
    
    done = 0
    start = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=15) as ex:
        futures = {ex.submit(process_book, item): item for item in need}
        for f in concurrent.futures.as_completed(futures):
            idx, cover_path, real = f.result()
            done += 1
            t = books[idx]['title'][:20]
            icon = "✅" if real else "🎨"
            print(f"[{done}/{len(need)}] {icon} {t}", flush=True)
            books[idx]['cover'] = cover_path
            if done % 80 == 0:
                save_data(data)
                print(f"  💾 保存 | {done}/{len(need)}", flush=True)
    
    save_data(data)
    elapsed = time.time() - start
    print(f"\n{'='*60}")
    print(f"✅ OpenLibrary: {stats['ok']} | 📚 Google: {stats['google_ok']} | 🎨 占位: {stats['google_fail']} | ⏭ 跳过: {stats['skip']}")
    print(f"⏱ {elapsed/60:.1f}分钟")

if __name__ == "__main__":
    main()
