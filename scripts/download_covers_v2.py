#!/usr/bin/env python3
"""增强版封面下载：支持 ISBN + 书名搜索 + 智能占位图"""
import json, os, re, time, urllib.request, urllib.parse, hashlib, concurrent.futures, threading, struct

BOOKLIST_DIR = "/home/gem/workspace/agent/workspace/my-booklist"
DATA_FILE = os.path.join(BOOKLIST_DIR, "js/data.js")
COVERS_DIR = os.path.join(BOOKLIST_DIR, "img/covers")
os.makedirs(COVERS_DIR, exist_ok=True)

stats = {"ok": 0, "fail": 0, "skip": 0, "placeholder": 0}
lock = threading.Lock()

# Color palettes for generated covers (bg, text)
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
    """Save data without eval wrapper"""
    with open(DATA_FILE) as f:
        content = f.read()
    eq = content.index('=')
    semi = content.rindex(';')
    new_content = content[:eq+1] + '\n' + json.dumps(data, ensure_ascii=False, indent=2) + content[semi:]
    with open(DATA_FILE, 'w') as f:
        f.write(new_content)

def download_from_openlibrary(isbn):
    """Try OpenLibrary by ISBN"""
    url = f"https://covers.openlibrary.org/b/isbn/{isbn}-L.jpg"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        resp = urllib.request.urlopen(req, timeout=6)
        data = resp.read()
        if len(data) > 2000:
            return True, data
    except:
        pass
    return False, None

def download_from_google(title, author):
    """Try Google Books by title + author"""
    query = title
    if author:
        # Clean author name
        author_clean = re.sub(r'[，,、].*', '', author).strip()
        if author_clean:
            query += " " + author_clean
    query = query[:100]  # Limit length
    
    encoded = urllib.parse.quote(query)
    url = f"https://www.googleapis.com/books/v1/volumes?q={encoded}&maxResults=1&printType=books"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        resp = urllib.request.urlopen(req, timeout=8)
        data = json.loads(resp.read().decode('utf-8'))
        if data.get('totalItems', 0) > 0:
            images = data['items'][0].get('volumeInfo', {}).get('imageLinks', {})
            for key in ['thumbnail', 'smallThumbnail']:
                if key in images:
                    img_url = images[key].replace('http:', 'https:')
                    # Try to get larger image
                    img_url = img_url.replace('zoom=1', 'zoom=2')
                    req2 = urllib.request.Request(img_url, headers={"User-Agent": "Mozilla/5.0"})
                    resp2 = urllib.request.urlopen(req2, timeout=8)
                    img_data = resp2.read()
                    if len(img_data) > 2000:
                        return True, img_data
    except:
        pass
    return False, None

def generate_placeholder(title, author, book_id):
    """Generate a simple colored SVG placeholder"""
    idx = book_id % len(COLORS)
    bg, fg = COLORS[idx]
    
    # Get first character
    first = ''
    if title:
        first = title.strip()[0:1]
    
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="200" height="300" viewBox="0 0 200 300">
  <rect width="200" height="300" fill="{bg}" rx="8"/>
  <text x="100" y="155" text-anchor="middle" fill="{fg}" font-size="48" font-weight="bold" font-family="system-ui,-apple-system,sans-serif">{first}</text>
  <text x="100" y="280" text-anchor="middle" fill="{fg}" font-size="10" opacity="0.6" font-family="system-ui,-apple-system,sans-serif">my-booklist</text>
</svg>'''
    return svg.encode('utf-8')

def process_book_with_isbn(book):
    """Process a book that has ISBN - try OpenLibrary"""
    isbn = book['isbn'].replace('-', '')
    filename = f"{isbn}.jpg"
    filepath = os.path.join(COVERS_DIR, filename)
    
    # Already downloaded?
    if os.path.exists(filepath) and os.path.getsize(filepath) > 2000:
        with lock: stats["skip"] += 1
        return filepath, True
    
    # Try OpenLibrary
    ok, data = download_from_openlibrary(isbn)
    if ok:
        with open(filepath, 'wb') as f:
            f.write(data)
        with lock: stats["ok"] += 1
        return filepath, True
    
    return None, False

def process_book_without_isbn(book):
    """Process a book without ISBN - try Google Books"""
    title = book.get('title', '')
    author = book.get('author', '')
    
    # Create a stable filename from title hash
    h = hashlib.md5(title.encode()).hexdigest()[:8]
    filename = f"title_{h}.jpg"
    filepath = os.path.join(COVERS_DIR, filename)
    
    # Already downloaded?
    if os.path.exists(filepath) and os.path.getsize(filepath) > 2000:
        with lock: stats["skip"] += 1
        return filepath, True
    
    # Try Google Books
    ok, data = download_from_google(title, author)
    if ok:
        with open(filepath, 'wb') as f:
            f.write(data)
        with lock: stats["ok"] += 1
        return filepath, True
    
    return None, False

def generate_placeholder_for_book(book):
    """Generate placeholder SVG"""
    title = book.get('title', '')
    author = book.get('author', '')
    h = hashlib.md5(title.encode()).hexdigest()[:8]
    filename = f"placeholder_{h}.svg"
    filepath = os.path.join(COVERS_DIR, filename)
    
    if not os.path.exists(filepath):
        svg_data = generate_placeholder(title, author, book['id'])
        with open(filepath, 'wb') as f:
            f.write(svg_data)
    
    with lock: stats["placeholder"] += 1
    return f"img/covers/{filename}"

def process_book(item):
    i, book = item
    cover = book.get('cover', '')
    isbn = book.get('isbn', '').replace('-', '')
    
    # If already has local cover (not openlibrary URL), skip
    if cover and cover.startswith('img/covers/'):
        filepath = os.path.join(BOOKLIST_DIR, cover)
        if os.path.exists(filepath):
            with lock: stats["skip"] += 1
            return i, cover, True
    
    # Try to get a real cover
    if isbn:
        path, ok = process_book_with_isbn(book)
        if ok:
            return i, f"img/covers/{os.path.basename(path)}", True
    
    path, ok = process_book_without_isbn(book)
    if ok:
        return i, f"img/covers/{os.path.basename(path)}", True
    
    # Fall back to placeholder
    placeholder_path = generate_placeholder_for_book(book)
    return i, placeholder_path, False

def main():
    data, _ = load_data()
    books = data['BOOKS']
    
    need = []
    for i, b in enumerate(books):
        cover = b.get('cover', '')
        isbn = b.get('isbn', '').replace('-', '')
        # Need cover if: no cover, or cover is openlibrary URL (not local), or cover file missing
        if not cover:
            need.append((i, b))
        elif cover.startswith('http'):
            need.append((i, b))
        elif cover.startswith('img/covers/'):
            filepath = os.path.join(BOOKLIST_DIR, cover)
            if not os.path.exists(filepath):
                need.append((i, b))
    
    has_isbn = sum(1 for _, b in need if b.get('isbn'))
    no_isbn = len(need) - has_isbn
    
    print(f"总书籍: {len(books)}")
    print(f"需要处理: {len(need)} (有ISBN: {has_isbn} | 无ISBN: {no_isbn})")
    print(f"并发: 10线程")
    print("=" * 60)
    
    done = 0
    start = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as ex:
        futures = {ex.submit(process_book, item): item for item in need}
        for f in concurrent.futures.as_completed(futures):
            idx, cover_path, real_cover = f.result()
            done += 1
            title = books[idx]['title'][:25]
            icon = "✅" if real_cover else "🎨"
            print(f"[{done}/{len(need)}] {icon} {title}", flush=True)
            
            # Update book's cover in data
            books[idx]['cover'] = cover_path
            
            if done % 100 == 0:
                save_data(data)
                elapsed = time.time() - start
                print(f"  💾 已保存 | {done}/{len(need)} | {elapsed/60:.1f}min", flush=True)
    
    save_data(data)
    elapsed = time.time() - start
    print(f"\n{'='*60}")
    print(f"✅ 实际封面: {stats['ok']} | 🎨 占位图: {stats['placeholder']} | ⏭ 跳过: {stats['skip']}")
    print(f"⏱ 耗时: {elapsed/60:.1f}分钟")

if __name__ == "__main__":
    main()
