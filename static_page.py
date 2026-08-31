"""生成静态 HTML 导航页面，供 nginx 直接展示（无需后端服务在线）

每次后台书签数据更新时调用 generate_static_page()，
将当前书签数据内嵌为 JSON 并渲染为独立 HTML 文件，
nginx 可直接托管该文件，实现离线可用的书签导航页。
"""
import json
import logging
import os
import time
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

# 分类图标
_CAT_ICONS = ['📂', '🎬', '📝', '💻', '🎮', '🎧', '🔧', '🏠', '📚', '💰',
              '🛒', '✈️', '🖼️', '👔', '🔗', '🌍', '📊', '🗂️', '⚙️', '🧰',
              '📁', '🔔', '📌', '🎯']

_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN" data-theme="dark">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>SeeTab 书签导航</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }

:root {
  --bg: #1a1a2e;
  --bg2: #16213e;
  --bg3: #0f3460;
  --card: rgba(255,255,255,0.06);
  --card-hover: rgba(255,255,255,0.1);
  --text: #e0e0e0;
  --text2: #a0a0b0;
  --primary: #7b8ad6;
  --primary-dark: #5b6abf;
  --border: rgba(255,255,255,0.08);
  --border-active: rgba(123,138,214,0.4);
  --shadow: 0 4px 20px rgba(0,0,0,0.3);
  --bm-icon-bg: rgba(123,138,214,0.12);
}

[data-theme="light"] {
  --bg: #ffffff;
  --bg2: #f8f9fa;
  --bg3: #f0f1f3;
  --card: rgba(255,255,255,0.95);
  --card-hover: rgba(255,255,255,1);
  --text: #1a2332;
  --text2: #5a6a7a;
  --primary: #5b6abf;
  --primary-dark: #4a57a3;
  --border: rgba(0,0,0,0.1);
  --border-active: rgba(91,106,191,0.4);
  --shadow: 0 4px 20px rgba(0,0,0,0.08);
  --bm-icon-bg: rgba(91,106,191,0.08);
}

html, body { height: 100%; }
body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Noto Sans SC", sans-serif;
  background: linear-gradient(135deg, var(--bg) 0%, var(--bg2) 50%, var(--bg3) 100%);
  color: var(--text);
  transition: background 0.4s, color 0.4s;
  min-height: 100vh;
}
[data-theme="light"] body { background: #ffffff; }

.topbar {
  position: sticky;
  top: 0;
  z-index: 100;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  background: transparent;
}
.topbar-title { font-size: 16px; font-weight: 700; }
.topbar-right { display: flex; align-items: center; gap: 12px; }

.theme-toggle, .repo-btn {
  width: 36px; height: 36px; border-radius: 8px;
  background: var(--card); display: flex; align-items: center; justify-content: center;
  cursor: pointer; transition: background 0.2s; color: var(--text2); font-size: 16px;
  border: 1px solid var(--border);
}
.theme-toggle:hover, .repo-btn:hover { background: var(--card-hover); color: var(--text); }

.repo-popup {
  position: fixed; top: 60px; right: 20px; z-index: 99999;
  background: var(--bg2); color: var(--text); border: 1px solid var(--border);
  border-radius: 8px; padding: 14px 36px 14px 18px; font-size: 14px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.25); max-width: calc(100vw - 40px);
  word-break: break-all; white-space: normal;
}
.repo-popup .repo-popup-label { display: block; font-size: 12px; color: var(--text2); margin-bottom: 6px; }
.repo-popup .repo-popup-url { color: var(--primary); text-decoration: none; }
.repo-popup .repo-popup-url:hover { text-decoration: underline; }
.repo-popup .repo-popup-close {
  position: absolute; top: 6px; right: 8px; cursor: pointer; font-size: 16px;
  line-height: 1; color: var(--text2); background: none; border: none; padding: 4px;
}
.repo-popup .repo-popup-close:hover { color: var(--text); }

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 8px 24px 48px;
}

.search-section { width: 100%; max-width: 600px; margin: 2vh auto 24px; }
.search-box { position: relative; width: 100%; }
.search-box .search-icon {
  position: absolute; left: 16px; top: 50%; transform: translateY(-50%); color: var(--text2);
}
.search-box input {
  width: 100%; padding: 14px 46px 14px 46px; border: 1px solid var(--border);
  border-radius: 24px; font-size: 16px; background: var(--card); color: var(--text);
  outline: none; transition: background 0.3s, border-color 0.3s, box-shadow 0.3s;
}
.search-box input:focus {
  background: var(--card-hover); border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(91,106,191,0.15);
}
.search-box input::placeholder { color: var(--text2); }

.category-grid { display: flex; flex-wrap: wrap; gap: 6px 4px; margin-bottom: 20px; }
.cat-card {
  display: inline-flex; align-items: center; gap: 6px; padding: 5px 12px;
  border-radius: 6px; cursor: pointer; border: 1px solid var(--border);
  transition: all 0.15s; user-select: none; white-space: nowrap; background: var(--card);
}
.cat-card:hover { background: var(--card-hover); border-color: var(--border-active); }
.cat-card.active { background: rgba(123,138,214,0.35); border-color: var(--border-active); }
[data-theme="light"] .cat-card.active { background: rgba(91,106,191,0.18); }
.cat-card .cat-icon { font-size: 14px; }
.cat-card .cat-name { font-size: 13px; font-weight: 600; line-height: 1.4; }
.cat-card .cat-count { font-size: 11px; color: var(--text2); }

.bookmark-panel { margin-bottom: 28px; }
.bookmark-panel-header {
  display: flex; align-items: center; gap: 10px; margin-bottom: 14px; padding: 0 4px;
}
.bookmark-panel-header .panel-icon { font-size: 20px; }
.bookmark-panel-header .panel-title { font-size: 16px; font-weight: 600; }
.bookmark-panel-header .panel-path { font-size: 12px; color: var(--text2); }
.bookmark-panel-header .panel-count { font-size: 12px; color: var(--text2); }
.bookmark-panel-header .panel-close {
  margin-left: auto; width: 28px; height: 28px; border-radius: 50%;
  background: var(--card); border: 1px solid var(--border); display: flex;
  align-items: center; justify-content: center; cursor: pointer; color: var(--text2);
  font-size: 14px; transition: all 0.2s;
}
.bookmark-panel-header .panel-close:hover { background: var(--card-hover); color: var(--text); }

.bookmark-grid {
  display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 10px;
}
.bookmark-item {
  display: flex; align-items: center; gap: 12px; padding: 10px 14px;
  background: var(--card); border-radius: 10px; border: 1px solid var(--border);
  cursor: pointer; text-decoration: none; color: var(--text);
  transition: background 0.2s, border-color 0.2s, transform 0.2s, box-shadow 0.2s;
}
.bookmark-item:hover {
  border-color: var(--primary); transform: translateY(-1px); box-shadow: var(--shadow);
  background: var(--card-hover);
}
.bookmark-item:hover .bm-title { color: var(--primary); }
.bookmark-item .bm-icon {
  width: 32px; height: 32px; border-radius: 8px; background: var(--bm-icon-bg);
  display: flex; align-items: center; justify-content: center; font-size: 13px;
  color: var(--primary); flex-shrink: 0; font-weight: 700; overflow: hidden;
}
.bookmark-item .bm-icon img { width: 20px; height: 20px; border-radius: 3px; }
.bookmark-item .bm-info { flex: 1; min-width: 0; }
.bookmark-item .bm-title {
  font-size: 13px; font-weight: 600; overflow: hidden; text-overflow: ellipsis;
  white-space: nowrap;
}
.bookmark-item .bm-url {
  font-size: 11px; color: var(--text2); margin-top: 2px; overflow: hidden;
  text-overflow: ellipsis; white-space: nowrap;
}

.ico-0 { color: #e74c3c; } .ico-1 { color: #e67e22; } .ico-2 { color: #f1c40f; } .ico-3 { color: #2ecc71; }
.ico-4 { color: #1abc9c; } .ico-5 { color: #3498db; } .ico-6 { color: #9b59b6; } .ico-7 { color: #e91e63; }

.empty { text-align: center; padding: 40px; color: var(--text2); font-size: 14px; }

.footer-bar {
  text-align: center; padding: 16px 12px; font-size: 11px; color: var(--text2); opacity: 0.7;
}

@media (max-width: 768px) {
  .category-grid { gap: 4px 3px; }
  .cat-card { padding: 4px 8px; font-size: 12px; }
  .bookmark-grid { grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); }
}
@media (max-width: 480px) {
  .bookmark-grid { grid-template-columns: 1fr; }
}
</style>
</head>
<body>

<div class="topbar">
  <div class="topbar-title">SeeTab</div>
  <div class="topbar-right">
    <div class="repo-btn" id="repoBtn" title="书签数据来源">
      <svg viewBox="0 0 24 24" width="18" height="18"><path d="M12 2C6.48 2 2 6.48 2 12c0 4.42 2.87 8.17 6.84 9.49.5.09.66-.22.66-.48 0-.24-.01-.87-.01-1.71-2.78.61-3.37-1.34-3.37-1.34-.45-1.16-1.11-1.47-1.11-1.47-.91-.62.07-.6.07-.6 1 .07 1.53 1.03 1.53 1.03.89 1.53 2.34 1.09 2.91.83.09-.65.35-1.09.63-1.34-2.22-.25-4.55-1.11-4.55-4.94 0-1.09.39-1.99 1.03-2.69-.1-.25-.45-1.27.1-2.65 0 0 .84-.27 2.75 1.02.8-.22 1.65-.33 2.5-.34.85.01 1.7.12 2.5.34 1.91-1.29 2.75-1.02 2.75-1.02.55 1.38.2 2.4.1 2.65.64.7 1.03 1.6 1.03 2.69 0 3.84-2.34 4.69-4.57 4.94.36.31.68.92.68 1.85 0 1.34-.01 2.42-.01 2.75 0 .27.16.58.67.48A10.02 10.02 0 0022 12c0-5.52-4.48-10-10-10z" fill="currentColor"/></svg>
    </div>
    <div class="theme-toggle" id="themeToggle" title="切换主题">
      <span id="themeIcon">🌙</span>
    </div>
  </div>
</div>

<div class="container">
  <div class="search-section">
    <div class="search-box">
      <svg class="search-icon" viewBox="0 0 24 24" width="20" height="20"><path d="M15.5 14h-.79l-.28-.27A6.471 6.471 0 0016 9.5 6.5 6.5 0 109.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z" fill="currentColor"/></svg>
      <input type="text" id="searchInput" placeholder="搜索书签..." autocomplete="off">
    </div>
  </div>

  <div id="content"></div>

  <div class="footer-bar" id="updateInfo"></div>
</div>

<script>
const DATA = __BOOKMARKS_JSON__;
const REPO_URL = __REPO_URL__;
const CAT_ICONS = __CAT_ICONS__;
const catIcon = i => CAT_ICONS[i % CAT_ICONS.length];

let allCategories = (DATA.categories || []).filter(c => c.category !== '__root_bookmarks__');
let validCategories = allCategories.filter(c => c.items.length > 0);
let activeCat = null;
let isSearchMode = false;

function escHtml(s) { const d = document.createElement('div'); d.textContent = s == null ? '' : String(s); return d.innerHTML; }
const escAttr = escHtml;
function catShortName(c) { return c.split(' / ').pop(); }
function stripCatPrefix(t) { const i = t.indexOf(' - '); return i > 0 ? t.substring(i + 3) : t; }
function cleanTitle(t) {
  if (!t) return '';
  let s = t.replace(/\\s*[-_|–—]\\s*(CSDN博客|博客园|简书|知乎|Stack Overflow|GitHub|Gitee|GitLab|Jenkins|Docker|Kubernetes|官方|官网|首页|Download|Documentation|Sign In|Login).*$/gi, '');
  s = s.replace(/\\s*[-_|–—]\\s*$/, '').trim();
  return s.length > 50 ? s.substring(0, 47) + '...' : (s || t);
}
function bmIconHtml(url, title) {
  try {
    const u = new URL(url);
    const fav = u.origin + '/favicon.ico';
    const letter = (title || u.hostname)[0].toUpperCase();
    return '<div class="bm-icon" data-fav="' + escAttr(fav) + '" data-letter="' + escAttr(letter) + '">' + letter + '</div>';
  } catch { return '<div class="bm-icon">?</div>'; }
}

let _favObserver = null;
function getFavObserver() {
  if (_favObserver) return _favObserver;
  _favObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      const el = entry.target;
      _favObserver.unobserve(el);
      const fav = el.dataset.fav;
      if (!fav) return;
      const img = new Image();
      img.onload = () => { el.innerHTML = ''; const i = document.createElement('img'); i.src = fav; el.appendChild(i); };
      img.onerror = () => {};
      img.src = fav;
    });
  }, { rootMargin: '200px' });
  return _favObserver;
}
function loadFavicons() {
  const icons = document.querySelectorAll('.bm-icon[data-fav]');
  if (!icons.length) return;
  const ob = getFavObserver();
  icons.forEach(el => ob.observe(el));
}

function renderMainView() {
  const content = document.getElementById('content');
  let html = '<div class="category-grid">';
  validCategories.forEach((cat, i) => {
    const sn = catShortName(cat.category);
    const isActive = activeCat === cat.category;
    html += '<div class="cat-card ' + (isActive ? 'active' : '') + '" data-cat="' + escAttr(cat.category) + '" data-idx="' + i + '">'
      + '<div class="cat-icon ico-' + (i % 8) + '">' + catIcon(i) + '</div>'
      + '<div class="cat-name">' + escHtml(sn) + '</div>'
      + '<div class="cat-count">' + cat.items.length + ' 书签</div></div>';
  });
  html += '</div>';
  if (activeCat) html += renderBookmarkPanel(activeCat);
  content.innerHTML = html;
  bindContentEvents();
  loadFavicons();
}

function renderBookmarkPanel(categoryName) {
  const cat = validCategories.find(c => c.category === categoryName);
  if (!cat) return '';
  const idx = validCategories.indexOf(cat);
  const sn = catShortName(categoryName);
  const parentPath = categoryName.includes(' / ') ? categoryName.substring(0, categoryName.lastIndexOf(' / ')) : '';
  let html = '<div class="bookmark-panel"><div class="bookmark-panel-header">';
  html += '<span class="panel-icon ico-' + (idx % 8) + '">' + catIcon(idx) + '</span>';
  html += '<span class="panel-title">' + escHtml(sn) + '</span>';
  if (parentPath) html += '<span class="panel-path">' + escHtml(parentPath) + '</span>';
  html += '<span class="panel-count">' + cat.items.length + ' 个书签</span>';
  html += '<div class="panel-close" data-action="close-panel">✕</div></div>';
  html += '<div class="bookmark-grid">';
  cat.items.forEach(item => {
    const t = escHtml(sn) + ' - ' + escHtml(cleanTitle(item.title));
    const u = escHtml(item.url);
    html += '<a class="bookmark-item" href="' + escAttr(item.url) + '" target="_blank" rel="noopener">'
      + bmIconHtml(item.url, item.title)
      + '<div class="bm-info"><div class="bm-title">' + t + '</div><div class="bm-url">' + u + '</div></div></a>';
  });
  html += '</div></div>';
  return html;
}

function toggleCategory(catName) {
  const wasActive = activeCat === catName;
  activeCat = wasActive ? null : catName;
  isSearchMode = false;
  const content = document.getElementById('content');
  content.querySelectorAll('.cat-card').forEach(card => {
    card.classList.toggle('active', card.dataset.cat === activeCat);
  });
  const oldPanel = content.querySelector('.bookmark-panel');
  if (oldPanel) oldPanel.remove();
  if (activeCat) {
    const grid = content.querySelector('.category-grid');
    const panelHtml = renderBookmarkPanel(activeCat);
    if (panelHtml) { grid.insertAdjacentHTML('afterend', panelHtml); loadFavicons(); }
  }
}

function closeBookmarkPanel() {
  activeCat = null;
  document.getElementById('content').querySelectorAll('.cat-card').forEach(c => c.classList.remove('active'));
  const panel = document.querySelector('.bookmark-panel');
  if (panel) panel.remove();
}

function performSearch(keyword) {
  const kws = keyword.toLowerCase().trim().split(/\\s+/).filter(Boolean);
  if (!kws.length) { isSearchMode = false; renderMainView(); return; }
  isSearchMode = true;
  activeCat = null;
  const matched = [];
  validCategories.forEach(cat => {
    const items = cat.items.filter(item =>
      kws.every(k => item.title.toLowerCase().includes(k) || item.url.toLowerCase().includes(k))
    );
    if (items.length) matched.push({ cat, items });
  });
  let html = '';
  if (matched.length) {
    html += '<div class="bookmark-grid">';
    matched.forEach(({ cat, items }) => {
      const sn = catShortName(cat.category);
      items.forEach(item => {
        html += '<a class="bookmark-item" href="' + escAttr(item.url) + '" target="_blank" rel="noopener">'
          + bmIconHtml(item.url, item.title)
          + '<div class="bm-info"><div class="bm-title">' + escHtml(sn) + ' - ' + escHtml(cleanTitle(item.title)) + '</div>'
          + '<div class="bm-url">' + escHtml(item.url) + '</div></div></a>';
      });
    });
    html += '</div>';
  } else {
    html += '<div class="empty">未找到匹配的书签</div>';
  }
  document.getElementById('content').innerHTML = html;
  loadFavicons();
}

let _bound = false;
function bindContentEvents() {
  if (_bound) return;
  _bound = true;
  document.getElementById('content').addEventListener('click', (e) => {
    if (e.target.closest('[data-action="close-panel"]')) { closeBookmarkPanel(); return; }
    const card = e.target.closest('.cat-card[data-cat]');
    if (card && !isSearchMode) { toggleCategory(card.dataset.cat); return; }
  });
  const input = document.getElementById('searchInput');
  let timer = null;
  input.addEventListener('input', () => {
    clearTimeout(timer);
    const v = input.value.trim();
    timer = setTimeout(() => performSearch(v), 200);
  });
}

function initTheme() {
  const theme = localStorage.getItem('theme') || 'dark';
  document.documentElement.setAttribute('data-theme', theme);
  document.getElementById('themeIcon').textContent = theme === 'dark' ? '🌙' : '☀️';
}
document.getElementById('themeToggle').addEventListener('click', () => {
  const cur = document.documentElement.getAttribute('data-theme') || 'dark';
  const next = cur === 'dark' ? 'light' : 'dark';
  document.documentElement.setAttribute('data-theme', next);
  localStorage.setItem('theme', next);
  document.getElementById('themeIcon').textContent = next === 'dark' ? '🌙' : '☀️';
});

document.getElementById('repoBtn').addEventListener('click', () => {
  const existed = document.querySelector('.repo-popup');
  if (existed) { existed.remove(); return; }
  if (!REPO_URL) {
    const p = document.createElement('div');
    p.className = 'repo-popup';
    p.innerHTML = '<span class="repo-popup-label">书签库地址</span>未配置<button class="repo-popup-close">✕</button>';
    document.body.appendChild(p);
    p.querySelector('.repo-popup-close').addEventListener('click', () => p.remove());
    return;
  }
  const p = document.createElement('div');
  p.className = 'repo-popup';
  p.innerHTML = '<span class="repo-popup-label">书签库地址</span><a class="repo-popup-url" target="_blank" rel="noopener"></a><button class="repo-popup-close">✕</button>';
  document.body.appendChild(p);
  const a = p.querySelector('.repo-popup-url'); a.href = REPO_URL; a.textContent = REPO_URL;
  p.querySelector('.repo-popup-close').addEventListener('click', () => p.remove());
});

initTheme();
const total = (DATA.categories || []).reduce((s, c) => s + (c.items ? c.items.length : 0), 0);
const updateTime = DATA.last_update ? new Date(DATA.last_update * 1000).toLocaleString('zh-CN') : '';
if (updateTime) document.getElementById('updateInfo').textContent = total + ' 书签 | 更新于 ' + updateTime;
renderMainView();
</script>
</body>
</html>
"""


def generate_static_page(
    bookmarks_data: List[Dict],
    last_update: float,
    output_path: str,
    repo_url: Optional[str] = None,
) -> bool:
    """根据当前书签数据生成静态 HTML 导航页面

    将书签数据内嵌为 JSON，渲染为独立 HTML 文件，供 nginx 直接托管。

    Args:
        bookmarks_data: 书签分类数据
        last_update: 最后更新时间戳
        output_path: 输出 HTML 文件路径
        repo_url: 书签库 Git 地址（可选）

    Returns:
        bool: 是否成功生成
    """
    if not output_path:
        logger.warning("静态页面输出路径为空，跳过生成")
        return False

    try:
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    except Exception as e:
        logger.error("创建静态页面输出目录失败: %s", e)
        return False

    try:
        data_json = json.dumps(
            {"categories": bookmarks_data, "last_update": last_update},
            ensure_ascii=False,
        )
        # 转义 JSON 中的 </script> 防止截断
        data_json = data_json.replace("</", "<\\/")

        repo_json = json.dumps(repo_url or "", ensure_ascii=False)
        cat_icons_json = json.dumps(_CAT_ICONS, ensure_ascii=False)

        html = _HTML_TEMPLATE \
            .replace("__BOOKMARKS_JSON__", data_json) \
            .replace("__REPO_URL__", repo_json) \
            .replace("__CAT_ICONS__", cat_icons_json)

        tmp_path = output_path + ".tmp"
        with open(tmp_path, "w", encoding="utf-8") as f:
            f.write(html)
        os.replace(tmp_path, output_path)

        logger.info("静态导航页面已生成: %s (分类 %d, 更新于 %s)",
                    output_path, len(bookmarks_data),
                    time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(last_update)) if last_update else "-")
        return True
    except Exception as e:
        logger.error("生成静态导航页面失败: %s", e)
        return False
