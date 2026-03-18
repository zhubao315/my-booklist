// my-booklist main application
(function() {
  'use strict';

  // ===== Data Cache =====
  var DataCache = {
    KEY: 'booklist_data',
    VERSION: '2026-03-18-v1',
    load: function() {
      try {
        var cached = JSON.parse(localStorage.getItem(this.KEY));
        if (cached && cached.version === this.VERSION) {
          return cached.data;
        }
      } catch(e) {}
      return null;
    },
    save: function(data) {
      try {
        localStorage.setItem(this.KEY, JSON.stringify({ version: this.VERSION, data: data }));
      } catch(e) { console.warn('DataCache save failed', e); }
    }
  };

  var DATA = window.DATA || DataCache.load();
  if (!DATA) { console.error('DATA not loaded'); return; }
  if (window.DATA) DataCache.save(window.DATA); // cache fresh load

  // ===== Book Cover Fetcher (Google Books API) =====
  var CoverCache = {
    KEY: 'booklist_covers_v2',
    _data: null,
    load: function() {
      if (this._data) return this._data;
      try { this._data = JSON.parse(localStorage.getItem(this.KEY)) || {}; }
      catch(e) { this._data = {}; }
      return this._data;
    },
    get: function(id) { return this.load()[id] || null; },
    set: function(id, url) { this.load()[id] = url; this._save(); },
    _save: function() {
      try { localStorage.setItem(this.KEY, JSON.stringify(this._data)); } catch(e) {}
    }
  };

  // Fetch cover from Google Books API
  function fetchCoverFromGoogle(title, author) {
    return new Promise(function(resolve) {
      var cleanTitle = title.replace(/[《》\s]/g, '').trim();
      var cleanAuthor = (author || '').replace(/[《》\s]/g, '').trim();
      // Use Chinese title for search
      var query = encodeURIComponent(cleanTitle);
      var url = 'https://www.googleapis.com/books/v1/volumes?q=' + query + '&maxResults=3&fields=items(volumeInfo(imageLinks))';
      var xhr = new XMLHttpRequest();
      xhr.open('GET', url, true);
      xhr.timeout = 8000;
      xhr.onload = function() {
        try {
          var data = JSON.parse(xhr.responseText);
          var items = data.items || [];
          for (var i = 0; i < items.length; i++) {
            var links = items[i].volumeInfo && items[i].volumeInfo.imageLinks;
            if (links) {
              // Prefer larger thumbnail
              var imgUrl = links.thumbnail || links.smallThumbnail;
              if (imgUrl) {
                // Upgrade to larger image if possible
                imgUrl = imgUrl.replace('zoom=1', 'zoom=2').replace('edge=curl', '');
                resolve(imgUrl);
                return;
              }
            }
          }
        } catch(e) {}
        resolve(null);
      };
      xhr.onerror = function() { resolve(null); };
      xhr.ontimeout = function() { resolve(null); };
      xhr.send();
    });
  }

  // Batch load covers with concurrency limit
  var coverQueue = [];
  var coverLoading = false;
  var coverConcurrency = 3;
  var coverActive = 0;

  function enqueueCover(book) {
    if (CoverCache.get(book.id)) return; // Already cached
    coverQueue.push(book);
    processCoverQueue();
  }

  function processCoverQueue() {
    while (coverActive < coverConcurrency && coverQueue.length > 0) {
      var book = coverQueue.shift();
      coverActive++;
      fetchCoverFromGoogle(book.title, book.author).then(function(url) {
        if (url) {
          CoverCache.set(book.id, url);
          updateBookCover(book.id, url);
        }
        coverActive--;
        processCoverQueue();
      });
    }
  }

  function updateBookCover(bookId, url) {
    var card = document.querySelector('.book-card[data-id="' + bookId + '"]');
    if (!card) return;
    // Check if cover already exists
    if (card.querySelector('.book-cover-wrap')) return;
    // Hide placeholder
    var placeholder = card.querySelector('.book-cover-placeholder');
    if (placeholder) placeholder.style.display = 'none';
    var wrap = document.createElement('div');
    wrap.className = 'book-cover-wrap';
    wrap.innerHTML = '<img class="book-cover loaded" src="' + url + '" alt="cover" loading="lazy" onerror="this.parentElement.remove()">';
    card.insertBefore(wrap, card.firstChild);
  }

  // State
  var state = {
    filteredBooks: [],
    currentPage: 1,
    perPage: 30,
    activeCategory: 1,
    activeStatus: 'all',
    searchQuery: '',
    sortBy: 'default',
    theme: localStorage.getItem('theme') || (window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark')
  };

  // DOM refs
  var $ = function(sel) { return document.querySelector(sel); };
  var $$ = function(sel) { return document.querySelectorAll(sel); };

  // Init
  function init() {
    applyTheme(state.theme);
    bindEvents();
    state.filteredBooks = DATA.BOOKS;
    renderBooks();

    renderStats();
    updateStatCards();
    initReadingProgress();
    registerSW();
  }

  // Theme
  function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    state.theme = theme;
    localStorage.setItem('theme', theme);
    var btn = $('#theme-toggle');
    if (btn) btn.textContent = theme === 'dark' ? '\u2600\uFE0F' : '\uD83C\uDF19';
  }
  function toggleTheme() {
    applyTheme(state.theme === 'dark' ? 'light' : 'dark');
  }

  // Reading progress bar
  function initReadingProgress() {
    var bar = $('#reading-progress');
    if (!bar) return;
    window.addEventListener('scroll', function() {
      var h = document.documentElement.scrollHeight - window.innerHeight;
      var p = h > 0 ? (window.scrollY / h) * 100 : 0;
      bar.style.width = p + '%';
    }, { passive: true });
  }

  // Stats
  function updateStatCards() {
    var books = DATA.BOOKS;
    var done = books.filter(function(b) { return b.status === 'done'; }).length;
    var notes = books.filter(function(b) { return b.hasNote; }).length;
    setText('#stat-total', books.length);
    setText('#stat-done', done);
    setText('#stat-notes', notes);
    setText('#stat-categories', Object.keys(DATA.CATEGORIES).length);
  }

  function renderStats() {
    var panel = $('#stats-panel');
    if (!panel) return;
    var books = DATA.BOOKS;
    var byCat = {};
    var byStatus = { done: 0, reading: 0, want: 0 };
    books.forEach(function(b) {
      byCat[b.category] = (byCat[b.category] || 0) + 1;
      byStatus[b.status]++;
    });
    var html = '<h3>\u9605\u8BFB\u7EDF\u8BA1 <button class="close-btn" id="close-stats">\u00D7</button></h3>';
    html += '<div class="stat-row"><span class="label">\u603B\u4E66\u7C4D</span><span class="value">' + books.length + '</span></div>';
    html += '<div class="stat-row"><span class="label">\u5DF2\u8BFB</span><span class="value" style="color:var(--purple)">' + byStatus.done + '</span></div>';
    html += '<div class="stat-row"><span class="label">\u5728\u8BFB</span><span class="value" style="color:var(--green)">' + byStatus.reading + '</span></div>';
    html += '<div class="stat-row"><span class="label">\u60F3\u8BFB</span><span class="value" style="color:var(--blue)">' + byStatus.want + '</span></div>';
    html += '<div class="stat-row"><span class="label">\u6709\u7B14\u8BB0</span><span class="value">' + books.filter(function(b){return b.hasNote}).length + '</span></div>';
    html += '<h4 style="margin-top:20px;color:var(--a)">\u5206\u7C7B\u7EDF\u8BA1</h4>';
    Object.keys(byCat).sort(function(a,b){return byCat[b]-byCat[a]}).forEach(function(cat) {
      html += '<div class="stat-row"><span class="label">' + esc(cat) + '</span><span class="value">' + byCat[cat] + '</span></div>';
    });
    panel.innerHTML = html;
    var closeBtn = document.getElementById('close-stats');
    if (closeBtn) closeBtn.addEventListener('click', function() { toggleStats(false); });
  }

  function toggleStats(open) {
    var panel = $('#stats-panel');
    var overlay = $('#stats-overlay');
    if (!panel) return;
    if (open === undefined) open = !panel.classList.contains('open');
    panel.classList.toggle('open', open);
    if (overlay) overlay.classList.toggle('open', open);
  }

  // Filter & Search
  // Show skeleton loading
  function showSkeleton(count) {
    var container = $('#book-grid');
    if (!container) return;
    var html = '';
    for (var i = 0; i < (count || 8); i++) {
      html += '<div class="skeleton-card"><div class="skeleton-line h20 w60"></div><div class="skeleton-line w80"></div><div class="skeleton-line w40"></div><div class="skeleton-line"></div></div>';
    }
    container.innerHTML = html;
  }

  function applyFilters() {
    var books = DATA.BOOKS;
    // Category filter
    if (state.activeCategory) {
      books = books.filter(function(b) { return b.categoryId === state.activeCategory; });
    }
    // Status filter
    if (state.activeStatus !== 'all') {
      books = books.filter(function(b) { return b.status === state.activeStatus; });
    }
    // Search
    if (state.searchQuery) {
      var q = state.searchQuery.toLowerCase();
      books = books.filter(function(b) {
        return (b.title && b.title.toLowerCase().indexOf(q) !== -1) ||
               (b.author && b.author.toLowerCase().indexOf(q) !== -1) ||
               (b.desc && b.desc.toLowerCase().indexOf(q) !== -1) ||
               (b.tags && b.tags.some(function(t) { return t.toLowerCase().indexOf(q) !== -1; }));
      });
    }
    // Sort
    switch (state.sortBy) {
      case 'title': books.sort(function(a,b) { return (a.title||'').localeCompare(b.title||''); }); break;
      case 'author': books.sort(function(a,b) { return (a.author||'').localeCompare(b.author||''); }); break;
      case 'rating': books.sort(function(a,b) { return (b.rating||0) - (a.rating||0); }); break;
      case 'category': books.sort(function(a,b) { return (a.category||'').localeCompare(b.category||'') || (a.title||'').localeCompare(b.title||''); }); break;
    }
    state.filteredBooks = books;
    state.currentPage = 1;
    renderBooks();
  }

  // Render books
  // Highlight search matches
  function hl(text, query) {
    if (!query || !text) return esc(text);
    var safe = esc(text);
    var escaped = query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    return safe.replace(new RegExp('(' + escaped + ')', 'gi'), '<mark>$1</mark>');
  }

  function renderBooks() {
    var container = $('#book-grid');
    var emptyState = $('#empty-state');
    var pageInfo = $('#page-info');
    var prevBtn = $('#prev-page');
    var nextBtn = $('#next-page');
    if (!container) return;

    var books = state.filteredBooks;
    var total = books.length;
    var pages = Math.ceil(total / state.perPage);
    var start = (state.currentPage - 1) * state.perPage;
    var end = start + state.perPage;
    var page = books.slice(start, end);

    if (total === 0) {
      container.innerHTML = '';
      if (emptyState) emptyState.style.display = 'block';
      if (pageInfo) pageInfo.textContent = '';
      return;
    }
    if (emptyState) emptyState.style.display = 'none';

    container.innerHTML = page.map(function(b) {
      var statusText = b.status === 'done' ? '\u5DF2\u8BFB' : (b.status === 'reading' ? '\u5728\u8BFB' : '\u60F3\u8BFB');
      var noteLink = b.hasNote && b.noteFile ? 'notes/' + b.noteFile : null;
      var coverUrl = b.cover || CoverCache.get(b.id);
      var card = '<div class="book-card" data-id="' + b.id + '">';
      if (coverUrl) {
        card += '<div class="book-cover-wrap"><img class="book-cover loaded" src="' + esc(coverUrl) + '" alt="' + esc(b.title.replace(/[《》\u300B]/g, '').replace(/[《\u300A]/g, '')) + '" loading="lazy" onerror="this.parentElement.style.display=\'none\'"></div>';
      } else {
        card += '<div class="book-cover-placeholder"><span>' + esc((b.title || '?').replace(/[《》\u300A\u300B]/g, '').charAt(0)) + '</span></div>';
      }
      card += '<span class="status-badge ' + b.status + '">' + statusText + '</span>';
      card += '<div class="book-card-header"><h3>' + hl(b.title, state.searchQuery) + '</h3></div>';
      card += '<p class="book-author">' + hl(b.author, state.searchQuery) + '</p>';
      card += '<p class="book-desc">' + hl(b.desc || '', state.searchQuery) + '</p>';
      card += '<div class="book-meta">';
      card += '<span class="tag cat">' + esc(b.category) + '</span>';
      card += '<span class="tag status-' + b.status + '">' + statusText + '</span>';
      if (b.hasNote) card += '<span class="tag has-note">\uD83D\uDCD6 \u6709\u7B14\u8BB0</span>';
      if (b.tags) b.tags.slice(0, 3).forEach(function(t) { card += '<span class="tag">' + esc(t) + '</span>'; });
      card += '</div></div>';
      if (noteLink) {
        card = '<a href="' + noteLink + '" style="text-decoration:none">' + card + '</a>';
      }
      return card;
    }).join('');

    // Enqueue cover fetching for books without covers (lazy, async)
    page.forEach(function(b) {
      if (!b.cover && !CoverCache.get(b.id)) {
        enqueueCover(b);
      }
    });

    // Section title & count
    var titleEl = document.querySelector('.section-title');
    if (titleEl) {
      var catNames = {1:'文学虚构类',2:'实用技能类',3:'认知成长类',4:'历史社科类',5:'科技科普类',6:'投资理财类',7:'传记人物类',8:'艺术美学类',9:'哲学宗教类'};
      titleEl.textContent = state.activeCategory ? catNames[state.activeCategory] || '筛选结果' : '全部书籍';
    }
    var countEl = $('#section-count');
    if (countEl) countEl.textContent = '\u5171 ' + total + ' \u672C';

    // Pagination
    if (pageInfo) pageInfo.textContent = state.currentPage + ' / ' + pages;
    if (prevBtn) prevBtn.disabled = state.currentPage <= 1;
    if (nextBtn) nextBtn.disabled = state.currentPage >= pages;
  }

  // Toast
  function showToast(msg) {
    var toast = $('#toast');
    if (!toast) return;
    toast.textContent = msg;
    toast.classList.add('show');
    setTimeout(function() { toast.classList.remove('show'); }, 2000);
  }

  // Keyboard shortcuts
  function handleKeydown(e) {
    // Don't intercept when typing in inputs
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
      if (e.key === 'Escape') { e.target.blur(); }
      return;
    }
    switch(e.key) {
      case '/':
        e.preventDefault();
        var search = $('#search-input');
        if (search) search.focus();
        break;
      case 'Escape':
        toggleStats(false);
        break;
      case 't':
        toggleTheme();
        showToast('\u4E3B\u9898\u5DF2\u5207\u6362');
        break;
      case 's':
        toggleStats();
        break;
    }
  }

  // Event bindings
  function bindEvents() {
    // Theme
    var themeBtn = $('#theme-toggle');
    if (themeBtn) themeBtn.addEventListener('click', toggleTheme);

    // Stats
    var statsBtn = $('#stats-toggle');
    if (statsBtn) statsBtn.addEventListener('click', function() { toggleStats(true); });
    var statsOverlay = $('#stats-overlay');
    if (statsOverlay) statsOverlay.addEventListener('click', function() { toggleStats(false); });

    // Search
    var searchInput = $('#search-input');
    if (searchInput) {
      var debounce;
      searchInput.addEventListener('input', function() {
        clearTimeout(debounce);
        debounce = setTimeout(function() {
          state.searchQuery = searchInput.value.trim();
          applyFilters();
        }, 300);
      });
    }

    // Category buttons
    $$('.category-btn').forEach(function(btn) {
      btn.addEventListener('click', function() {
        $$('.category-btn').forEach(function(b) { b.classList.remove('active'); });
        btn.classList.add('active');
        state.activeCategory = btn.dataset.cat === 'all' ? 0 : parseInt(btn.dataset.cat) || 0;
        // Sync mobile select
        var sel = $('#category-select');
        if (sel) sel.value = state.activeCategory || 'all';
        showSkeleton(6);
        requestAnimationFrame(function() { applyFilters(); });
      });
    });

    // Mobile category select
    var catSelect = $('#category-select');
    if (catSelect) catSelect.addEventListener('change', function() {
      var val = this.value;
      state.activeCategory = val === 'all' ? 0 : parseInt(val);
      // Sync desktop buttons
      $$('.category-btn').forEach(function(b) {
        b.classList.toggle('active', parseInt(b.dataset.cat) === state.activeCategory);
      });
      showSkeleton(6);
      requestAnimationFrame(function() { applyFilters(); });
    });

    // Pagination
    var prevBtn = $('#prev-page');
    var nextBtn = $('#next-page');
    if (prevBtn) prevBtn.addEventListener('click', function() {
      if (state.currentPage > 1) { state.currentPage--; renderBooks(); window.scrollTo({top: 300, behavior: 'smooth'}); }
    });
    if (nextBtn) nextBtn.addEventListener('click', function() {
      var pages = Math.ceil(state.filteredBooks.length / state.perPage);
      if (state.currentPage < pages) { state.currentPage++; renderBooks(); window.scrollTo({top: 300, behavior: 'smooth'}); }
    });

    // Keyboard
    document.addEventListener('keydown', handleKeydown);
  }

  // Helpers
  function esc(s) {
    if (!s) return '';
    var d = document.createElement('div');
    d.textContent = s;
    return d.innerHTML;
  }
  function setText(sel, text) {
    var el = $(sel);
    if (el) el.textContent = text;
  }

  // Service Worker
  function registerSW() {
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.register('sw.js').catch(function() {});
    }
  }

  // Boot
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
