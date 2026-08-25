#!/bin/bash
# 生成 INTERNAL Chrome 扩展（CRX3 + 固定 Extension ID + Preferences 安装）
# 流程：源码 → 生成 .pem → 打包 CRX3 → 计算 ID → 写 Preferences → 放到 Extensions/ID/Version/
# 用法: ./build_crx.sh
#   环境变量:
#     CHROME_USER_DATA  Chrome 用户目录（默认: ~/Library/Application Support/Google/Chrome）
#     CHROME_PROFILE    Profile 名（默认: Default）
#     INSTALL_CHROME=1  自动写入 Chrome 用户目录并复制 .crx（默认: 仅生成本地产物）

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
EXT_DIR="$SCRIPT_DIR/extension"
DIST_DIR="$SCRIPT_DIR/dist"
KEY_DIR="$DIST_DIR/keys"
KEY_PATH="$KEY_DIR/seetab.pem"

CHROME_USER_DATA="${CHROME_USER_DATA:-$HOME/Library/Application Support/Google/Chrome}"
CHROME_PROFILE="${CHROME_PROFILE:-Default}"
INSTALL_CHROME="${INSTALL_CHROME:-0}"

# 从 version.txt 读取版本号
VERSION=$(cat "$SCRIPT_DIR/version.txt" | tr -d '[:space:]')
if [ -z "$VERSION" ]; then
  echo "错误: version.txt 为空或不存在"
  exit 1
fi
echo "==> 版本号: ${VERSION}（来源: version.txt）"

# 同步 manifest 版本号
sed -i '' "s/\"version\": \"[^\"]*\"/\"version\": \"${VERSION}\"/" "$EXT_DIR/manifest.json"

# === 1. 生成固定 .pem 私钥（仅首次）===
if [ ! -f "$KEY_PATH" ]; then
  echo "==> 未找到 .pem，生成新的 RSA 2048 私钥: $KEY_PATH"
  mkdir -p "$KEY_DIR"
  openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:2048 -out "$KEY_PATH"
  echo "    私钥已生成（dist/ 已被 .gitignore 忽略，不会进入 git）"
else
  echo "==> 使用已有私钥: $KEY_PATH"
fi

# === 2. 打包 CRX3 并计算 Extension ID ===
echo "==> 打包 CRX3..."
CRX_DIR="$DIST_DIR/crx-internal"
mkdir -p "$CRX_DIR"
CRX_FILE="$CRX_DIR/seetab-v${VERSION}.crx"

# 第一步：打包（状态信息打到 stderr）
python3 "$SCRIPT_DIR/pack_crx.py" \
  --src "$EXT_DIR" \
  --key "$KEY_PATH" \
  --out "$CRX_FILE" >&2

# 第二步：单独取出 Extension ID（用于路径）
EXT_ID=$(python3 "$SCRIPT_DIR/pack_crx.py" --key "$KEY_PATH" --src "$EXT_DIR" --out /dev/null --id-only)
echo "==> Extension ID: $EXT_ID"

# === 3. 生成 Extensions/ID/Version/ 目录结构（本地）===
LOCAL_EXT_DIR="$CRX_DIR/Extensions/$EXT_ID/$VERSION"
mkdir -p "$LOCAL_EXT_DIR"
cp "$CRX_FILE" "$LOCAL_EXT_DIR/seetab.crx"
echo "==> 本地产物布局:"
echo "    $LOCAL_EXT_DIR/seetab.crx"

# === 4. 生成 Preferences 片段 JSON ===
# 该片段需要合并到 <user-data>/Default/Preferences 的 extensions.settings.<ID> 下
PREF_SNIPPET="$CRX_DIR/Preferences.snippet.json"
MANIFEST_HASH=$(python3 -c "
import hashlib, json, sys
with open('$EXT_DIR/manifest.json','rb') as f:
    data = f.read()
print(hashlib.sha256(data).hexdigest())
")

# 构造 extensions.settings.<ID> 条目（Chrome 期望的字段）
python3 -c "
import json
ext_id = '$EXT_ID'
version = '$VERSION'
crx_path = '$LOCAL_EXT_DIR/seetab.crx'
manifest_hash = '$MANIFEST_HASH'
entry = {
    'state': 1,
    'location': 4,
    'path': crx_path,
    'manifest': {
        'name': 'SeeTab',
        'version': version,
        'manifest_version': 3,
        'description': 'SeeTab 新标签页',
        'chrome_url_overrides': {'newtab': 'newtab.html'},
        'permissions': ['storage', 'alarms', 'bookmarks'],
        'host_permissions': ['<all_urls>'],
        'icons': {
            '16': 'icons/icon16.png',
            '48': 'icons/icon48.png',
            '128': 'icons/icon128.png',
        },
        'background': {'service_worker': 'background.js'},
        'options_page': 'options.html',
    },
    'path_9': crx_path,
    'was_installed_by_default': True,
    'from_bookmark': False,
    'from_webstore': False,
    'acknowledged': True,
    'install_time': 0,
    'install_param': '',
    'manifest_mtime': 0,
    'active_permissions': {
        'api_permissions': ['storage', 'alarms', 'bookmarks'],
        'explicit_host': ['<all_urls>'],
        'manifest_permissions': [],
    },
    'granted_permissions': {
        'api_permissions': ['storage', 'alarms', 'bookmarks'],
        'explicit_host': ['<all_urls>'],
        'manifest_permissions': [],
    },
    'content_settings': [],
    'content_pack': '',
    'pack_context': '',
    'commands': {},
}
snippet = {'extensions': {'settings': {ext_id: entry}}}
with open('$PREF_SNIPPET', 'w') as f:
    json.dump(snippet, f, indent=2, ensure_ascii=False)
"
echo "==> Preferences 片段: $PREF_SNIPPET"

# === 5. （可选）安装到 Chrome 用户目录 ===
if [ "$INSTALL_CHROME" = "1" ]; then
  echo ""
  echo "==> 安装到 Chrome 用户目录: $CHROME_USER_DATA / $CHROME_PROFILE"
  if [ ! -d "$CHROME_USER_DATA/$CHROME_PROFILE" ]; then
    echo "错误: Chrome profile 目录不存在: $CHROME_USER_DATA/$CHROME_PROFILE"
    echo "      请用 CHROME_USER_DATA / CHROME_PROFILE 环境变量指定"
    exit 1
  fi

  # 复制 .crx 到 Chrome 的 Extensions/<ID>/<Version>/ 目录
  CHROME_EXT_DIR="$CHROME_USER_DATA/$CHROME_PROFILE/Extensions/$EXT_ID/$VERSION"
  mkdir -p "$CHROME_EXT_DIR"
  cp "$CRX_FILE" "$CHROME_EXT_DIR/seetab.crx"
  echo "    已复制: $CHROME_EXT_DIR/seetab.crx"

  # 备份并合并 Preferences
  PREF_FILE="$CHROME_USER_DATA/$CHROME_PROFILE/Preferences"
  BACKUP_FILE="$PREF_FILE.backup-$(date +%Y%m%d-%H%M%S)"
  echo "    备份 Preferences → $BACKUP_FILE"
  cp "$PREF_FILE" "$BACKUP_FILE"

  python3 -c "
import json, sys

pref_file = '$PREF_FILE'
snippet_file = '$PREF_SNIPPET'

with open(pref_file, 'r', encoding='utf-8') as f:
    prefs = json.load(f)
with open(snippet_file, 'r', encoding='utf-8') as f:
    snippet = json.load(f)

ext_id = '$EXT_ID'
# 用 snippet 中的 path 替换为 Chrome 内实际路径
snippet_entry = snippet['extensions']['settings'][ext_id]
chrome_path = '$CHROME_EXT_DIR/seetab.crx'
snippet_entry['path'] = chrome_path
snippet_entry['path_9'] = chrome_path

prefs.setdefault('extensions', {}).setdefault('settings', {})
prefs['extensions']['settings'][ext_id] = snippet_entry

with open(pref_file, 'w', encoding='utf-8') as f:
    json.dump(prefs, f, ensure_ascii=False)
print('    Preferences 已更新')
"

  echo ""
  echo "==> 安装完成！"
  echo "    1. 完全退出 Chrome（Cmd+Q）"
  echo "    2. 重新启动 Chrome，扩展应自动加载"
  echo "    3. 如需回滚，恢复备份: cp $CHROME_USER_DATA/$CHROME_PROFILE/Preferences.backup-* $PREF_FILE"
  exit 0
fi

# === 默认：仅输出本地产物 + 安装说明 ===
echo ""
echo "==> 本地产物（不修改 Chrome 目录）:"
echo "    CRX3:           $CRX_FILE"
echo "    Extensions 目录: $LOCAL_EXT_DIR/"
echo "    Preferences 片段: $PREF_SNIPPET"
echo ""
echo "==> 手动安装到 Chrome:"
echo "    1. 完全退出 Chrome（Cmd+Q）"
echo "    2. 复制 .crx 到 Chrome 目录:"
echo "         cp -r $LOCAL_EXT_DIR $CHROME_USER_DATA/$CHROME_PROFILE/Extensions/$EXT_ID/"
echo "    3. 把 Preferences.snippet.json 的 extensions.settings.<ID> 条目合并到"
echo "       $CHROME_USER_DATA/$CHROME_PROFILE/Preferences"
echo "       （注意：path 字段改为 Chrome 内实际路径）"
echo "    4. 重启 Chrome"
echo ""
echo "    或用环境变量自动安装:"
echo "         INSTALL_CHROME=1 ./build_crx.sh"
echo ""
echo "==> Extension ID（固定）: $EXT_ID"
