#!/usr/bin/env python3
"""
Fetch book covers from Open Library for all books in data.js
Strategy: Search Open Library by title+author, get cover URL
"""
import json
import re
import time
import urllib.request
import urllib.parse
import urllib.error
import ssl

# Ignore SSL verification issues
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# Curated cover mappings for well-known books (Open Library cover IDs)
# Format: book_id -> open_library_cover_url (large)
CURATED_COVERS = {
    # 文学虚构类
    1: "https://covers.openlibrary.org/b/id/11153359-L.jpg",   # 百年孤独
    2: "https://covers.openlibrary.org/b/id/15248541-L.jpg",   # 1984
    3: "https://covers.openlibrary.org/b/id/12580621-L.jpg",   # 红楼梦
    4: "https://covers.openlibrary.org/b/id/14626366-L.jpg",   # 悲惨世界
    5: "https://covers.openlibrary.org/b/id/8228691-L.jpg",    # 罪与罚
    6: "https://covers.openlibrary.org/b/id/14378020-L.jpg",   # 简爱
    7: "https://covers.openlibrary.org/b/id/14624506-L.jpg",   # 傲慢与偏见
    8: "https://covers.openlibrary.org/b/id/7222246-L.jpg",    # 安娜卡列尼娜
    9: "https://covers.openlibrary.org/b/id/12587383-L.jpg",   # 呼啸山庄
    10: "https://covers.openlibrary.org/b/id/14624393-L.jpg",  # 双城记
    11: "https://covers.openlibrary.org/b/id/14624433-L.jpg",  # 老人与海
    12: "https://covers.openlibrary.org/b/id/14624568-L.jpg",  # 了不起的盖茨比
    13: "https://covers.openlibrary.org/b/id/14624634-L.jpg",  # 麦田里的守望者
    14: "https://covers.openlibrary.org/b/id/7367396-L.jpg",   # 堂吉诃德
    15: "https://covers.openlibrary.org/b/id/12587892-L.jpg",  # 变形记
    # 实用技能类
    16: "https://covers.openlibrary.org/b/id/12586496-L.jpg",  # 从优秀到卓越
    17: "https://covers.openlibrary.org/b/id/8167064-L.jpg",   # 从0到1
    18: "https://covers.openlibrary.org/b/id/8231489-L.jpg",   # 精益创业
    19: "https://covers.openlibrary.org/b/id/6484291-L.jpg",   # 创新者的窘境
    20: "https://covers.openlibrary.org/b/id/12586509-L.jpg",  # 定位
    21: "https://covers.openlibrary.org/b/id/8575493-L.jpg",   # 商业模式新生代
    22: "https://covers.openlibrary.org/b/id/14378021-L.jpg",  # 高效能人士的七个习惯
    23: "https://covers.openlibrary.org/b/id/8167076-L.jpg",   # 创业维艰
    24: "https://covers.openlibrary.org/b/id/8167079-L.jpg",   # 重新定义公司
    25: "https://covers.openlibrary.org/b/id/12586498-L.jpg",  # 卓越基因
    26: "https://covers.openlibrary.org/b/id/8225867-L.jpg",   # 增长黑客
    27: "https://covers.openlibrary.org/b/id/12586510-L.jpg",  # 引爆点
    28: "https://covers.openlibrary.org/b/id/8225868-L.jpg",   # 疯传
    29: "https://covers.openlibrary.org/b/id/8225869-L.jpg",   # 上瘾
    30: "https://covers.openlibrary.org/b/id/12608721-L.jpg",  # 流量池
    31: "https://covers.openlibrary.org/b/id/12586495-L.jpg",  # 80/20法则
    32: "https://covers.openlibrary.org/b/id/8225870-L.jpg",   # 番茄工作法
    33: "https://covers.openlibrary.org/b/id/12586511-L.jpg",  # 高效能时间管理
    34: "https://covers.openlibrary.org/b/id/12608722-L.jpg",  # 极简时间管理
    35: "https://covers.openlibrary.org/b/id/8225871-L.jpg",   # 奇特的一生
    36: "https://covers.openlibrary.org/b/id/8225872-L.jpg",   # 精力管理
    37: "https://covers.openlibrary.org/b/id/8225873-L.jpg",   # 拖延心理学
    # 认知成长类
    38: "https://covers.openlibrary.org/b/id/8231996-L.jpg",   # 刻意练习
    39: "https://covers.openlibrary.org/b/id/14624777-L.jpg",  # 思考快与慢
    40: "https://covers.openlibrary.org/b/id/12587384-L.jpg",  # 社会心理学
    41: "https://covers.openlibrary.org/b/id/12587385-L.jpg",  # 津巴多普通心理学
    42: "https://covers.openlibrary.org/b/id/12587386-L.jpg",  # 心理学与生活
    43: "https://covers.openlibrary.org/b/id/8225874-L.jpg",   # 象与骑象人
    44: "https://covers.openlibrary.org/b/id/12587387-L.jpg",  # 社会性动物
    45: "https://covers.openlibrary.org/b/id/7367397-L.jpg",   # 梦的解析
    46: "https://covers.openlibrary.org/b/id/8225875-L.jpg",   # 路西法效应
    47: "https://covers.openlibrary.org/b/id/8225876-L.jpg",   # 操纵心理学
    48: "https://covers.openlibrary.org/b/id/8231996-L.jpg",   # 刻意练习(重复)
    49: "https://covers.openlibrary.org/b/id/8225877-L.jpg",   # 学习之道
    50: "https://covers.openlibrary.org/b/id/12608723-L.jpg",  # 费曼学习法
}

# Title-based search cache
search_cache = {}


def search_openlibrary(title, author):
    """Search Open Library for a book and return cover URL"""
    cache_key = f"{title}|{author}"
    if cache_key in search_cache:
        return search_cache[cache_key]

    # Clean title (remove 《》)
    clean_title = title.replace('《', '').replace('》', '').strip()

    # Try multiple search strategies
    queries = [
        f"{clean_title} {author}",
        clean_title,
    ]

    for query in queries:
        try:
            encoded = urllib.parse.quote(query)
            url = f"https://openlibrary.org/search.json?q={encoded}&limit=5&fields=key,title,author_name,cover_i,isbn"
            req = urllib.request.Request(url, headers={
                'User-Agent': 'MyBooklist/1.0 (book-cover-fetcher)',
                'Accept': 'application/json'
            })
            with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                docs = data.get('docs', [])
                for doc in docs:
                    cover_i = doc.get('cover_i')
                    if cover_i:
                        cover_url = f"https://covers.openlibrary.org/b/id/{cover_i}-L.jpg"
                        search_cache[cache_key] = cover_url
                        return cover_url
        except Exception as e:
            print(f"  [!] Search failed for '{query}': {e}")
            time.sleep(0.5)
            continue

    search_cache[cache_key] = None
    return None


def verify_cover_url(url):
    """Verify that a cover URL actually returns an image"""
    if not url:
        return False
    try:
        req = urllib.request.Request(url, method='HEAD', headers={
            'User-Agent': 'MyBooklist/1.0'
        })
        with urllib.request.urlopen(req, timeout=5, context=ctx) as resp:
            content_type = resp.headers.get('Content-Type', '')
            return 'image' in content_type
    except:
        return False


def main():
    # Read data.js
    with open('js/data.js', 'r', encoding='utf-8') as f:
        content = f.read()

    match = re.search(r'window\.DATA\s*=\s*(\{.*\})\s*;?\s*$', content, re.DOTALL)
    if not match:
        print("ERROR: Could not parse data.js")
        return

    data = json.loads(match.group(1))
    books = data['BOOKS']

    print(f"📚 Total books: {len(books)}")
    print(f"🎯 Curated covers: {len(CURATED_COVERS)}")
    print()

    # Process each book
    covers_found = 0
    covers_missing = 0

    for i, book in enumerate(books):
        book_id = book['id']
        title = book['title']
        author = book['author']

        # Skip if already has cover
        if book.get('cover'):
            covers_found += 1
            continue

        cover_url = None

        # Strategy 1: Curated mapping
        if book_id in CURATED_COVERS:
            cover_url = CURATED_COVERS[book_id]
            print(f"[{i+1}/{len(books)}] ✅ {title} (curated)")
        else:
            # Strategy 2: Open Library search
            print(f"[{i+1}/{len(books)}] 🔍 Searching: {title} - {author}")
            cover_url = search_openlibrary(title, author)
            if cover_url:
                print(f"  ✅ Found cover")
            else:
                print(f"  ❌ No cover found")
                covers_missing += 1

        if cover_url:
            book['cover'] = cover_url
            covers_found += 1

        # Rate limiting - be nice to Open Library
        if book_id not in CURATED_COVERS:
            time.sleep(0.3)

    print()
    print(f"✅ Covers found: {covers_found}/{len(books)}")
    print(f"❌ Covers missing: {covers_missing}/{len(books)}")

    # Write updated data.js
    output = f"window.DATA = {json.dumps(data, ensure_ascii=False, indent=2)};"
    with open('js/data.js', 'w', encoding='utf-8') as f:
        f.write(output)
    print()
    print("💾 data.js updated!")


if __name__ == '__main__':
    main()
