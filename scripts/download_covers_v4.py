#!/usr/bin/env python3
"""封面下载 V4 - GitHub Actions版：OpenLibrary + Google Books"""
import json, os, time, urllib.request, urllib.parse, hashlib, concurrent.futures, threading

BOOKLIST_DIR = os.environ.get("GITHUB_WORKSPACE", "/home/gem/workspace/agent/workspace/my-booklist")
DATA_FILE = os.path.join(BOOKLIST_DIR, "js/data.js")
COVERS_DIR = os.path.join(BOOKLIST_DIR, "img/covers")
os.makedirs(COVERS_DIR, exist_ok=True)

limit = int(os.environ.get("LIMIT", "0"))
stats = {"ok": 0, "google": 0, "fail": 0, "skip": 0}
lock = threading.Lock()

COLORS = [
    ("#E8A838","#FFF"),("#4A6FA5","#FFF"),("#E84B4B","#FFF"),
    ("#2D6A4F","#FFF"),("#6B4E8A","#FFF"),("#D4A373","#FFF"),
    ("#2C3E50","#FFF"),("#E74C3C","#FFF"),("#1ABC9C","#FFF"),
    ("#9B59B6","#FFF"),("#F39C12","#FFF"),("#3498DB","#FFF"),
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
    new = content[:eq+1] + '\n' + json.dumps(data, ensure_ascii=False, separators=(',',':')) + content[semi:]
    with open(DATA_FILE, 'w') as f:
        f.write(new)

def download(url, timeout=10):
    req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0 (X11; Linux x86_64)"})
    resp = urllib.request.urlopen(req, timeout=timeout)
    return resp.read()

def try_openlibrary(isbn):
    try:
        data = download(f"https://covers.openlibrary.org/b/isbn/{isbn}-L.jpg")
        return data if len(data) > 3000 else None
    except: return None

def try_google(title, author):
    try:
        q = (title + " " + author.split('，')[0].split(',')[0].split('、')[0].strip())[:80]
        url = f"https://www.googleapis.com/books/v1/volumes?q={urllib.parse.quote(q)}&maxResults=1"
        resp = download(url)
        items = json.loads(resp).get('items', [])
        if items:
            imgs = items[0].get('volumeInfo',{}).get('imageLinks',{})
            for k in ['thumbnail','smallThumbnail']:
                if k in imgs:
                    img = download(imgs[k].replace('http:','https:'))
                    return img if len(img) > 2000 else None
    except: return None

def placeholder(title, bid):
    bg, fg = COLORS[bid % len(COLORS)]
    ch = title.strip()[0] if title else '?'
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="200" height="300"><rect width="200" height="300" fill="{bg}" rx="8"/><text x="100" y="155" text-anchor="middle" fill="{fg}" font-size="48" font-weight="bold" font-family="system-ui">{ch}</text></svg>'.encode()

def process(item):
    i, b = item
    isbn = b.get('isbn','').replace('-','')
    title = b.get('title','')
    fn = f"{isbn}.jpg" if isbn else f"t_{hashlib.md5(title.encode()).hexdigest()[:8]}.jpg"
    fp = os.path.join(COVERS_DIR, fn)
    
    if os.path.exists(fp) and os.path.getsize(fp) > 2000:
        with lock: stats["skip"] += 1
        return i, f"img/covers/{fn}", True
    
    # Try OpenLibrary
    if isbn:
        r = try_openlibrary(isbn)
        if r:
            with open(fp,'wb') as f: f.write(r)
            with lock: stats["ok"] += 1
            return i, f"img/covers/{fn}", True
    
    # Try Google Books
    r = try_google(title, b.get('author',''))
    if r:
        with open(fp,'wb') as f: f.write(r)
        with lock: stats["google"] += 1
        return i, f"img/covers/{fn}", True
    
    # Placeholder SVG
    ph = f"placeholder_{hashlib.md5(title.encode()).hexdigest()[:8]}.svg"
    ph_fp = os.path.join(COVERS_DIR, ph)
    if not os.path.exists(ph_fp):
        with open(ph_fp,'wb') as f: f.write(placeholder(title, b['id']))
    with lock: stats["fail"] += 1
    return i, f"img/covers/{ph}", False

def main():
    data, _ = load_data()
    books = data['BOOKS']
    if limit > 0: books = books[:limit]
    
    need = []
    for i, b in enumerate(data['BOOKS']):
        if limit > 0 and i >= limit: break
        c = b.get('cover','')
        if c.startswith('img/covers/'):
            fp = os.path.join(BOOKLIST_DIR, c)
            if os.path.exists(fp) and os.path.getsize(fp) > 2000: continue
        need.append((i, b))
    
    print(f"Total: {len(books)} | Need: {len(need)}")
    done = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as ex:
        futs = {ex.submit(process, it): it for it in need}
        for f in concurrent.futures.as_completed(futs):
            idx, cp, real = f.result()
            done += 1
            t = data['BOOKS'][idx]['title'][:20]
            print(f"[{done}/{len(need)}] {'✅' if real else '🎨'} {t}", flush=True)
            data['BOOKS'][idx]['cover'] = cp
            if done % 50 == 0: save_data(data)
    
    save_data(data)
    print(f"\n✅ OpenLibrary: {stats['ok']} | 📚 Google: {stats['google']} | 🎨 Placeholder: {stats['fail']} | ⏭ Skipped: {stats['skip']}")

if __name__ == "__main__":
    main()
