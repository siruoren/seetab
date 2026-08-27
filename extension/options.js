// 设置页面逻辑

const DEFAULTS = {
  serverUrl: 'http://192.168.31.120:5005',
  apiPassword: '',
  updateInterval: 5,
  enableWallpaper: true,
  searchEngine: 'bing',
  theme: 'dark',
  weatherCity: '',
  locale: 'auto'
};

// 内部请求时将协议转为浏览器 fetch 支持的 http/https
function toFetchUrl(url) {
  let u = url.replace(/^tcp:\/\//i, 'http://');
  if (!/^https?:\/\//i.test(u)) u = 'http://' + u;
  return u;
}

// 通过 background 代理 fetch
function proxyFetch(url, options) {
  return new Promise((resolve, reject) => {
    chrome.runtime.sendMessage({ type: 'proxyFetch', url, options }, resp => {
      if (!resp) { reject(new Error(t('background.noResponse'))); return; }
      if (resp.error) { reject(new Error(resp.error)); return; }
      resolve({
        ok: resp.ok,
        status: resp.status,
        json: () => Promise.resolve(JSON.parse(resp.body)),
        text: () => Promise.resolve(resp.body)
      });
    });
  });
}

// 验证地址格式
function isValidUrl(url) {
  const httpUrl = toFetchUrl(url);
  try { new URL(httpUrl); return true; } catch { return false; }
}

// 加载配置
function loadConfig() {
  chrome.storage.local.get(DEFAULTS, config => {
    document.getElementById('serverUrl').value = config.serverUrl;
    document.getElementById('apiPassword').value = config.apiPassword;
    document.getElementById('updateInterval').value = config.updateInterval;
    document.getElementById('enableWallpaper').checked = config.enableWallpaper;
    document.getElementById('searchEngine').value = config.searchEngine;
    document.getElementById('theme').value = config.theme;
    document.getElementById('weatherCity').value = config.weatherCity;
    document.getElementById('locale').value = config.locale;
    updateStatus();
  });
}

// 保存配置
function saveConfig() {
  const serverUrl = document.getElementById('serverUrl').value.trim().replace(/\/+$/, '');
  const apiPassword = document.getElementById('apiPassword').value;
  const updateInterval = parseInt(document.getElementById('updateInterval').value) || 5;
  const enableWallpaper = document.getElementById('enableWallpaper').checked;
  const searchEngine = document.getElementById('searchEngine').value;
  const theme = document.getElementById('theme').value;
  const weatherCity = document.getElementById('weatherCity').value.trim();
  const locale = document.getElementById('locale').value;

  if (!serverUrl) {
    showStatus(t('settings.error.serverUrlRequired'), 'error');
    return;
  }

  if (!isValidUrl(serverUrl)) {
    showStatus(t('settings.error.serverUrlInvalid'), 'error');
    return;
  }

  if (updateInterval < 1 || updateInterval > 1440) {
    showStatus(t('settings.error.intervalRange'), 'error');
    return;
  }

  chrome.storage.local.set({ serverUrl, apiPassword, updateInterval, enableWallpaper, searchEngine, theme, weatherCity, locale }, () => {
    showStatus(t('settings.saved'), 'success');
    updateStatus();
  });
}

// 测试连接
async function testConnection() {
  const serverUrl = document.getElementById('serverUrl').value.trim().replace(/\/+$/, '');
  const apiPassword = document.getElementById('apiPassword').value;

  if (!serverUrl) {
    showStatus(t('settings.error.serverUrlFirst'), 'error');
    return;
  }

  const fetchUrl = toFetchUrl(serverUrl);

  showStatus(t('settings.testing'), '');
  const statusEl = document.getElementById('status');
  statusEl.className = 'status';

  const headers = {};
  if (apiPassword) {
    headers['X-API-Key'] = apiPassword;
  }

  try {
    const resp = await proxyFetch(`${fetchUrl}/api/update_time`, { headers });

    if (resp.ok) {
      const bmResp = await proxyFetch(`${fetchUrl}/api/bookmarks`, { headers });
      if (bmResp.ok) {
        const data = await bmResp.json();
        showStatus(t('settings.connectionSuccess', data.total || 0), 'success');
      } else if (bmResp.status === 401) {
        showStatus(t('settings.error.authFailed'), 'error');
      } else {
        showStatus(t('settings.error.fetchFailed', bmResp.status), 'error');
      }
    } else if (resp.status === 401) {
      showStatus(t('settings.error.authFailed'), 'error');
    } else if (resp.status === 501) {
      showStatus(t('settings.error.server501'), 'error');
    } else {
      showStatus(t('settings.error.httpFailed', resp.status), 'error');
    }
  } catch (e) {
    if (e.name === 'TimeoutError') {
      showStatus(t('settings.error.timeout'), 'error');
    } else if (e.message && (e.message.includes('Failed to fetch') || e.message.includes('NetworkError'))) {
      showStatus(t('settings.error.network'), 'error');
    } else {
      showStatus(t('settings.error.connectionFailed', e.message), 'error');
    }
  }
}

// 立即同步
function triggerSync() {
  showStatus(t('settings.syncing'), 'success');
  chrome.runtime.sendMessage({ type: 'triggerSync' }, resp => {
    if (resp && resp.ok) {
      showStatus(t('settings.syncSuccess'), 'success');
      updateStatus();
    } else {
      showStatus(t('settings.syncFailed'), 'error');
    }
  });
}

// 更新状态显示
function updateStatus() {
  chrome.runtime.sendMessage({ type: 'getStatus' }, status => {
    if (!status) return;

    const configEl = document.getElementById('statusConfig');
    const totalEl = document.getElementById('statusTotal');
    const fetchEl = document.getElementById('statusLastFetch');

    configEl.textContent = status.configured ? t('settings.configured') : t('settings.notConfigured');
    configEl.style.color = status.configured ? '#2ecc71' : '#e74c3c';

    totalEl.textContent = status.total > 0 ? `${status.total}` : '-';

    if (status.lastUpdate > 0) {
      const d = new Date(status.lastUpdate * 1000);
      fetchEl.textContent = d.toLocaleString(getDateLocale());
    } else if (status.lastFetch > 0) {
      const d = new Date(status.lastFetch);
      fetchEl.textContent = d.toLocaleString(getDateLocale());
    } else {
      fetchEl.textContent = t('settings.neverSynced');
    }
  });

  // 同步状态时一并拉取后台服务的代码库地址
  fetchRepoUrl();
}

// 获取后台服务书签来源 Git 仓库地址并显示
async function fetchRepoUrl() {
  const repoEl = document.getElementById('statusRepoUrl');
  if (!repoEl) return;

  const { serverUrl, apiPassword } = await new Promise(resolve => {
    chrome.storage.local.get({ serverUrl: '', apiPassword: '' }, resolve);
  });
  if (!serverUrl) { repoEl.textContent = t('repo.noRepo'); return; }

  try {
    const headers = apiPassword ? { 'X-API-Key': apiPassword } : {};
    const resp = await proxyFetch(`${toFetchUrl(serverUrl)}/api/repo`, { headers });
    if (!resp.ok) { repoEl.textContent = t('repo.fetchFailed'); return; }
    const data = await resp.json();
    const url = (data && data.repo_url) || '';
    if (!url) { repoEl.textContent = t('repo.noRepo'); return; }
    // 仓库地址可点击跳转
    repoEl.innerHTML = '';
    const a = document.createElement('a');
    a.href = url;
    a.textContent = url;
    a.target = '_blank';
    a.rel = 'noopener';
    a.style.color = 'var(--primary, #7b8ad6)';
    a.style.wordBreak = 'break-all';
    repoEl.appendChild(a);
  } catch (e) {
    repoEl.textContent = t('repo.fetchFailed');
  }
}

// 显示状态消息
function showStatus(msg, type) {
  const el = document.getElementById('status');
  el.textContent = msg;
  el.className = `status ${type}`;
}

// 切换密码可见
document.getElementById('togglePwd').addEventListener('click', () => {
  const input = document.getElementById('apiPassword');
  const btn = document.getElementById('togglePwd');
  if (input.type === 'password') {
    input.type = 'text';
    btn.textContent = '🔒';
  } else {
    input.type = 'password';
    btn.textContent = '👁';
  }
});

// 语言切换实时生效
document.getElementById('locale').addEventListener('change', (e) => {
  const locale = e.target.value;
  setLocale(locale === 'auto' ? detectLocale() : locale);
  applyI18n();
  document.documentElement.lang = getLocale() === 'zh' ? 'zh-CN' : 'en';
});

// 绑定按钮事件
document.getElementById('saveBtn').addEventListener('click', saveConfig);
document.getElementById('testBtn').addEventListener('click', testConnection);
document.getElementById('syncBtn').addEventListener('click', triggerSync);

// 初始化
initLocale().then(() => {
  applyI18n();
  document.documentElement.lang = getLocale() === 'zh' ? 'zh-CN' : 'en';
  loadConfig();
});
