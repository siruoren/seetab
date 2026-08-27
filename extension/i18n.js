// === i18n 国际化模块 ===
// 根据浏览器语言自动选择中英文，后台可手动配置

const I18N = {
  zh: {
    // HTML 静态文本
    'title.newtab': '新标签页',
    'search.placeholder': '搜索书签或输入网址...',
    'search.clear': '清空',
    'search.go': '搜索',
    'weather.city.placeholder': '输入城市',
    'theme.toggle': '切换主题',
    'bookmark.save.title': '保存远程书签到本地',
    'bookmark.export.title': '导出远程书签为HTML',
    'settings.title': '设置',

    // 动态文本
    'recent.title': '最近使用',
    'bookmark.count': '书签',
    'bookmark.count.full': '个书签',
    'search.noResults': '未找到匹配的书签',
    'search.engine.hint': '在 {0} 中搜索「{1}」',
    'info.updateInfo': '{0} 书签 | 更新于 {1}',
    'error.noBackend': '未配置后端地址或无法连接',
    'error.noBackend.hint': '请点击右上角设置按钮进行配置',
    'error.noBackend.web': '无法连接后端服务',

    // 保存书签
    'bookmark.save.none': '没有远程书签可保存',
    'bookmark.save.allExist': '所有 {0} 个远程书签已存在于本地，无需添加',
    'bookmark.save.complete': '保存完成：新增 {0} 个，跳过 {1} 个已存在',
    'bookmark.save.failed': '保存失败：{0}',
    'bookmark.save.noApi': '当前环境不支持浏览器书签API',
    'bookmark.save.noBar': '无法获取书签栏',
    'error.timeout': '操作超时',
    'background.noResponse': 'background 无响应',

    // 导出书签
    'bookmark.export.none': '没有远程书签可导出',
    'bookmark.export.complete.dup': '已导出 {0} 个书签（跳过 {1} 个重复），请在浏览器中导入',
    'bookmark.export.complete': '已导出 {0} 个书签，请在浏览器中导入',
    'bookmark.export.failed': '导出失败：{0}',
    'bookmark.bar': '书签栏',
    'bookmark.browser': '浏览器书签',

    // 天气
    'weather.sunny': '晴',
    'weather.cloudy': '多云',
    'weather.overcast': '阴',
    'weather.rain': '雨',
    'weather.snow': '雪',
    'weather.fog': '雾',
    'weather.thunderstorm': '雷阵雨',
    'weather.lightRain': '小雨',
    'weather.shower': '阵雨',
    'weather.windy': '大风',

    // 搜索引擎
    'search.engine.baidu': '百度',

    // 设置页
    'settings.header': 'SeeTab 设置',
    'settings.backend': '后端服务配置',
    'settings.serverUrl': '服务地址',
    'settings.serverUrl.placeholder': 'http://192.168.31.120:5005',
    'settings.serverUrl.desc': '后端书签服务的完整地址（含端口），不带末尾斜杠',
    'settings.apiPassword': '访问密码',
    'settings.apiPassword.placeholder': '可选，后端配置的 API Key',
    'settings.apiPassword.desc': '与后端 config.yml 中 api_key 对应，未设置则留空',
    'settings.updateInterval': '更新间隔（分钟）',
    'settings.updateInterval.desc': '后台自动同步书签数据的时间间隔，最少 1 分钟',
    'settings.appearance': '外观设置',
    'settings.language': '显示语言',
    'settings.language.auto': '自动（跟随浏览器）',
    'settings.language.zh': '中文',
    'settings.language.en': 'English',
    'settings.language.desc': '设置界面和导航页的显示语言',
    'settings.theme': '主题',
    'settings.theme.dark': '暗色',
    'settings.theme.light': '亮色',
    'settings.theme.desc': '新标签页的明暗主题',
    'settings.weatherCity': '天气城市',
    'settings.weatherCity.placeholder': '如：北京、上海、Shenzhen',
    'settings.weatherCity.desc': '用于显示天气信息，留空则不显示',
    'settings.wallpaper': 'Bing 每日壁纸',
    'settings.wallpaper.desc': '启用后将使用 Bing 每日壁纸作为背景，禁用则使用默认纯色背景',
    'settings.searchEngine': '搜索引擎',
    'settings.searchEngine.desc': '搜索框回车或点击搜索按钮时使用的搜索引擎',
    'settings.syncStatus': '同步状态',
    'settings.configStatus': '配置状态',
    'settings.notConfigured': '未配置',
    'settings.configured': '已配置',
    'settings.cacheCount': '缓存书签数',
    'settings.lastSync': '上次同步',
    'settings.testConnection': '测试连接',
    'settings.syncNow': '立即同步',
    'settings.saveConfig': '保存配置',
    'settings.togglePassword': '显示/隐藏',
    'settings.saved': '配置已保存',
    'settings.testing': '正在测试连接...',
    'settings.syncing': '同步中...',
    'settings.syncSuccess': '同步成功',
    'settings.syncFailed': '同步请求失败',
    'settings.neverSynced': '从未同步',
    'settings.connectionSuccess': '连接成功! 共 {0} 个书签',
    'settings.error.serverUrlRequired': '请输入服务地址',
    'settings.error.serverUrlFirst': '请先输入服务地址',
    'settings.error.serverUrlInvalid': '服务地址格式不正确',
    'settings.error.intervalRange': '更新间隔需在 1-1440 分钟之间',
    'settings.error.authFailed': '认证失败: 密码不正确',
    'settings.error.fetchFailed': '连接成功（服务器可达），但获取书签失败: HTTP {0}',
    'settings.error.server501': '服务器返回 501：请确认后端服务运行正常，且 FRP 代理类型为 http 而非 tcp',
    'settings.error.httpFailed': '连接失败: HTTP {0}',
    'settings.error.timeout': '连接超时，请检查地址是否正确、服务是否运行',
    'settings.error.network': '网络错误：请检查地址是否可达，若使用 FRP 隧道请确认代理类型为 http',
    'settings.error.connectionFailed': '连接失败: {0}',
    'backend.online': '后台服务正常',
    'backend.offline': '后台服务不可用',

    // 代码库地址
    'repo.title': '代码库地址',
    'repo.url': '代码库地址',
    'repo.noRepo': '未配置',
    'repo.fetchFailed': '获取代码库地址失败',
    'repo.tooltip': '书签数据来源',
    'repo.empty': '后端未配置 Git 仓库地址',
  },

  en: {
    // HTML static
    'title.newtab': 'New Tab',
    'search.placeholder': 'Search bookmarks or enter URL...',
    'search.clear': 'Clear',
    'search.go': 'Search',
    'weather.city.placeholder': 'Enter city',
    'theme.toggle': 'Toggle theme',
    'bookmark.save.title': 'Save remote bookmarks to local',
    'bookmark.export.title': 'Export remote bookmarks as HTML',
    'settings.title': 'Settings',

    // Dynamic
    'recent.title': 'Recent',
    'bookmark.count': 'bookmarks',
    'bookmark.count.full': 'bookmarks',
    'search.noResults': 'No matching bookmarks found',
    'search.engine.hint': 'Search "{1}" on {0}',
    'info.updateInfo': '{0} bookmarks | Updated {1}',
    'error.noBackend': 'Backend not configured or unreachable',
    'error.noBackend.hint': 'Click the settings icon in the top right to configure',
    'error.noBackend.web': 'Cannot connect to backend service',

    // Save bookmarks
    'bookmark.save.none': 'No remote bookmarks to save',
    'bookmark.save.allExist': 'All {0} remote bookmarks already exist locally',
    'bookmark.save.complete': 'Saved: {0} new, {1} skipped (already exist)',
    'bookmark.save.failed': 'Save failed: {0}',
    'bookmark.save.noApi': 'Browser bookmarks API not available',
    'bookmark.save.noBar': 'Cannot access bookmark bar',
    'error.timeout': 'Operation timed out',
    'background.noResponse': 'Background no response',

    // Export bookmarks
    'bookmark.export.none': 'No remote bookmarks to export',
    'bookmark.export.complete.dup': 'Exported {0} bookmarks ({1} duplicates skipped). Import them in your browser.',
    'bookmark.export.complete': 'Exported {0} bookmarks. Import them in your browser.',
    'bookmark.export.failed': 'Export failed: {0}',
    'bookmark.bar': 'Bookmarks Bar',
    'bookmark.browser': 'Browser Bookmarks',

    // Weather
    'weather.sunny': 'Sunny',
    'weather.cloudy': 'Cloudy',
    'weather.overcast': 'Overcast',
    'weather.rain': 'Rain',
    'weather.snow': 'Snow',
    'weather.fog': 'Fog',
    'weather.thunderstorm': 'Thunderstorm',
    'weather.lightRain': 'Light Rain',
    'weather.shower': 'Showers',
    'weather.windy': 'Windy',

    // Search engine
    'search.engine.baidu': 'Baidu',

    // Settings
    'settings.header': 'SeeTab Settings',
    'settings.backend': 'Backend Service',
    'settings.serverUrl': 'Server URL',
    'settings.serverUrl.placeholder': 'http://192.168.31.120:5005',
    'settings.serverUrl.desc': 'Full address of backend bookmark service (with port), no trailing slash',
    'settings.apiPassword': 'API Key',
    'settings.apiPassword.placeholder': 'Optional, API key configured in backend',
    'settings.apiPassword.desc': 'Corresponds to api_key in backend config.yml. Leave empty if not set.',
    'settings.updateInterval': 'Update Interval (minutes)',
    'settings.updateInterval.desc': 'Auto-sync interval for bookmark data, minimum 1 minute',
    'settings.appearance': 'Appearance',
    'settings.language': 'Display Language',
    'settings.language.auto': 'Auto (follow browser)',
    'settings.language.zh': '中文',
    'settings.language.en': 'English',
    'settings.language.desc': 'Set the display language for the UI and new tab page',
    'settings.theme': 'Theme',
    'settings.theme.dark': 'Dark',
    'settings.theme.light': 'Light',
    'settings.theme.desc': 'Color scheme for the new tab page',
    'settings.weatherCity': 'Weather City',
    'settings.weatherCity.placeholder': 'e.g. Beijing, Shanghai, Shenzhen',
    'settings.weatherCity.desc': 'Used for weather display. Leave empty to hide.',
    'settings.wallpaper': 'Bing Daily Wallpaper',
    'settings.wallpaper.desc': 'Use Bing daily wallpaper as background. Disable for solid color.',
    'settings.searchEngine': 'Search Engine',
    'settings.searchEngine.desc': 'Search engine used when pressing Enter or clicking search',
    'settings.syncStatus': 'Sync Status',
    'settings.configStatus': 'Configuration',
    'settings.notConfigured': 'Not configured',
    'settings.configured': 'Configured',
    'settings.cacheCount': 'Cached bookmarks',
    'settings.lastSync': 'Last sync',
    'settings.testConnection': 'Test Connection',
    'settings.syncNow': 'Sync Now',
    'settings.saveConfig': 'Save',
    'settings.togglePassword': 'Show/Hide',
    'settings.saved': 'Configuration saved',
    'settings.testing': 'Testing connection...',
    'settings.syncing': 'Syncing...',
    'settings.syncSuccess': 'Sync successful',
    'settings.syncFailed': 'Sync request failed',
    'settings.neverSynced': 'Never synced',
    'settings.connectionSuccess': 'Connected! {0} bookmarks total',
    'settings.error.serverUrlRequired': 'Please enter server URL',
    'settings.error.serverUrlFirst': 'Please enter server URL first',
    'settings.error.serverUrlInvalid': 'Invalid server URL format',
    'settings.error.intervalRange': 'Update interval must be between 1-1440 minutes',
    'settings.error.authFailed': 'Authentication failed: incorrect API key',
    'settings.error.fetchFailed': 'Server reachable, but failed to fetch bookmarks: HTTP {0}',
    'settings.error.server501': 'Server returned 501: ensure backend is running and FRP proxy type is http, not tcp',
    'settings.error.httpFailed': 'Connection failed: HTTP {0}',
    'settings.error.timeout': 'Connection timed out. Check the URL and ensure the service is running.',
    'settings.error.network': 'Network error: check if the URL is reachable. If using FRP tunnel, ensure proxy type is http.',
    'settings.error.connectionFailed': 'Connection failed: {0}',
    'backend.online': 'Backend service online',
    'backend.offline': 'Backend service offline',

    // Repository URL
    'repo.title': 'Repository URL',
    'repo.url': 'Repository URL',
    'repo.noRepo': 'Not configured',
    'repo.fetchFailed': 'Failed to fetch repository URL',
    'repo.tooltip': 'Bookmark data source',
    'repo.empty': 'Backend has no Git repository configured',
  }
};

let _locale = 'zh';

// 检测浏览器语言
function detectLocale() {
  const lang = navigator.language || (navigator.languages && navigator.languages[0]) || 'zh';
  return lang.startsWith('zh') ? 'zh' : 'en';
}

// 初始化语言（插件用 chrome.storage，web 用 localStorage）
async function initLocale() {
  const stored = await _getStorage('locale', 'auto');
  _locale = stored === 'auto' ? detectLocale() : stored;
}

function _getStorage(key, defaultValue) {
  if (typeof chrome !== 'undefined' && chrome.storage && chrome.storage.local) {
    return new Promise(resolve => {
      chrome.storage.local.get({ [key]: defaultValue }, result => resolve(result[key]));
    });
  }
  return Promise.resolve(localStorage.getItem(key) || defaultValue);
}

// 翻译函数
function t(key, ...args) {
  const dict = I18N[_locale] || I18N.zh;
  let s = dict[key] || I18N.zh[key] || key;
  args.forEach((arg, i) => {
    s = s.replace(`{${i}}`, arg);
  });
  return s;
}

function getLocale() { return _locale; }
function setLocale(locale) { _locale = locale; }
function getDateLocale() { return _locale === 'zh' ? 'zh-CN' : 'en-US'; }

// 获取天气描述（根据当前语言）
function getWeatherDesc(code) {
  const codes = {
    0:'weather.sunny', 1:'weather.sunny', 2:'weather.cloudy', 3:'weather.cloudy',
    45:'weather.fog', 48:'weather.fog',
    51:'weather.lightRain', 53:'weather.lightRain', 55:'weather.lightRain',
    61:'weather.rain', 63:'weather.rain', 65:'weather.rain',
    71:'weather.snow', 73:'weather.snow', 75:'weather.snow',
    80:'weather.shower', 81:'weather.shower', 82:'weather.shower',
    95:'weather.thunderstorm', 96:'weather.thunderstorm', 99:'weather.thunderstorm'
  };
  return t(codes[code] || 'weather.sunny');
}

// 获取天气图标
const _weatherIcons = {
  '晴': '☀️', '多云': '⛅', '阴': '☁️', '雨': '🌧️',
  '雪': '❄️', '雾': '🌫️', '雷阵雨': '⛈️', '小雨': '🌦️', '大风': '💨',
  'Sunny': '☀️', 'Cloudy': '⛅', 'Overcast': '☁️', 'Rain': '🌧️',
  'Snow': '❄️', 'Fog': '🌫️', 'Thunderstorm': '⛈️', 'Light Rain': '🌦️', 'Showers': '🌦️', 'Windy': '💨'
};

function getWeatherIcon(desc) {
  for (const key in _weatherIcons) {
    if (desc.includes(key)) return _weatherIcons[key];
  }
  return '🌤️';
}

// 应用静态 HTML 文本翻译
function applyI18n() {
  // 设置 HTML lang 属性
  document.documentElement.lang = _locale === 'zh' ? 'zh-CN' : 'en';

  // 翻译所有 data-i18n 元素
  document.querySelectorAll('[data-i18n]').forEach(el => {
    el.textContent = t(el.dataset.i18n);
  });
  // 翻译所有 data-i18n-placeholder 元素
  document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
    el.placeholder = t(el.dataset.i18nPlaceholder);
  });
  // 翻译所有 data-i18n-title 元素
  document.querySelectorAll('[data-i18n-title]').forEach(el => {
    el.title = t(el.dataset.i18nTitle);
  });
  // 翻译所有 data-i18n-html 元素（支持 HTML 内容）
  document.querySelectorAll('[data-i18n-html]').forEach(el => {
    el.innerHTML = t(el.dataset.i18nHtml);
  });
}
