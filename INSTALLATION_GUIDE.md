# 安裝與驗證指南

## 快速安裝

### 步驟 1: 複製 Skill 到 Claude Code 目錄

```bash
# 從專案根目錄執行
cp -r package-upgrade ~/.claude/skills/

# 或者如果你想測試,先複製到臨時位置
# cp -r package-upgrade ~/.claude/skills/package-upgrade-test
```

### 步驟 2: 設定執行權限

```bash
chmod +x ~/.claude/skills/package-upgrade/scripts/*.sh
chmod +x ~/.claude/skills/package-upgrade/scripts/*.py
```

### 步驟 3: 安裝依賴套件

```bash
pip install pipdeptree requests
```

---

## 驗證安裝

### 方法 1: 使用驗證腳本 (推薦)

```bash
# 執行驗證腳本
bash verify_installation.sh
```

這個腳本會自動檢查:
- ✅ Skill 目錄是否存在
- ✅ 所有必要檔案是否存在
- ✅ Scripts 是否有執行權限
- ✅ Python scripts 格式是否正確
- ✅ Python 依賴是否安裝
- ✅ SKILL.md frontmatter 是否正確

### 方法 2: 手動驗證步驟

#### 2.1 檢查檔案結構

```bash
# 檢查 Skill 目錄
ls -la ~/.claude/skills/package-upgrade/

# 應該看到:
# - LICENSE
# - README.md
# - SKILL.md
# - scripts/ (7 個檔案: 4 個 .sh + 3 個 .py)
# - references/ (5 個 .md 檔案)
# - templates/ (1 個 .md 檔案)
```

#### 2.2 檢查 SKILL.md frontmatter

```bash
head -15 ~/.claude/skills/package-upgrade/SKILL.md

# 應該看到:
# ---
# name: package-upgrade
# description: >
#   升級 Python 套件或修復 CVE 漏洞的完整工作流...
# ---
```

#### 2.3 檢查 Scripts 執行權限

```bash
ls -la ~/.claude/skills/package-upgrade/scripts/

# 所有 .sh 和 .py 檔案應該有 'x' 權限
# 例: -rwxr-xr-x  detect_env.sh
```

#### 2.4 檢查 Python Scripts

```bash
ls -la ~/.claude/skills/package-upgrade/scripts/*.py

# 應該看到 Python 檔案:
# -rwxr-xr-x  ast_scanner.py
# -rwxr-xr-x  dep_tree.py
# -rwxr-xr-x  fetch_changelog.py
```

#### 2.5 測試 Helper Scripts

```bash
# 測試 detect_env.sh
bash ~/.claude/skills/package-upgrade/scripts/detect_env.sh .

# 應該輸出 JSON,例:
# {
#   "pkg_manager": "pip",
#   "python_version": "3.11.4",
#   ...
# }
```

```bash
# 測試 dep_tree.py
python3 ~/.claude/skills/package-upgrade/scripts/dep_tree.py . requests

# 應該輸出 JSON (如果專案有 requests)
```

```bash
# 測試 ast_scanner.py  
python3 ~/.claude/skills/package-upgrade/scripts/ast_scanner.py . requests

# 應該輸出 JSON
```

#### 2.6 檢查 Python 依賴

```bash
# 檢查 pipdeptree
pipdeptree --version

# 檢查 requests
python3 -c "import requests; print(requests.__version__)"
```

### 方法 3: 在 Claude Code 中驗證

#### 3.1 啟動 Claude Code

```bash
claude
```

#### 3.2 列出 Skills

在 Claude Code 中輸入:
```
list available skills
```

或
```
show me all skills
```

你應該會看到 `package-upgrade` 出現在列表中。

#### 3.3 查看 Skill 資訊

```
show me the package-upgrade skill
```

或
```
tell me about the package-upgrade skill
```

Claude Code 應該會顯示 skill 的描述和觸發條件。

#### 3.4 測試觸發 Skill (Dry Run)

```
檢查這個專案能不能升級 requests 套件
```

或
```
分析一下升級 requests 會有什麼影響
```

**注意**: 不要直接說「升級 requests」,因為會真的執行升級!

---

## 常見問題排除

### Q1: 找不到 Skill

**症狀**: Claude Code 中看不到 package-upgrade

**檢查**:
```bash
# 確認目錄存在
ls ~/.claude/skills/package-upgrade/SKILL.md

# 確認 frontmatter 格式正確
head -15 ~/.claude/skills/package-upgrade/SKILL.md
```

**解決**:
- 確保 SKILL.md 的 frontmatter 使用 `---` 包圍
- 確保 `name: package-upgrade` 沒有多餘空格
- 重啟 Claude Code

### Q2: "Permission denied" 執行 scripts

**症狀**: 執行 helper scripts 時出現 Permission denied

**解決**:
```bash
chmod +x ~/.claude/skills/package-upgrade/scripts/*.sh
chmod +x ~/.claude/skills/package-upgrade/scripts/*.py
```

### Q3: Python scripts 找不到

**症狀**: 執行 Python scripts 時找不到檔案

**檢查**:
```bash
ls -la ~/.claude/skills/package-upgrade/scripts/*.py
```

**解決**:
確保 Python 檔案存在且有執行權限:

```bash
# 如果檔案缺失,從原始專案複製
cp /path/to/package-upgrade/scripts/*.py ~/.claude/skills/package-upgrade/scripts/

# 設定執行權限
chmod +x ~/.claude/skills/package-upgrade/scripts/*.py
```

### Q4: 缺少依賴

**症狀**: ModuleNotFoundError: No module named 'pipdeptree'

**解決**:
```bash
pip install pipdeptree requests
```

### Q5: jq 命令找不到

**症狀**: detect_env.sh 執行時出現 `jq: command not found`

**解決**:
```bash
# macOS
brew install jq

# Ubuntu/Debian
sudo apt-get install jq

# 其他系統
# https://stedolan.github.io/jq/download/
```

---

## 進階驗證: 完整測試

如果你想要完整測試 Skill 的功能,可以在一個測試專案中試用:

### 建立測試專案

```bash
# 建立測試目錄
mkdir -p /tmp/test-package-upgrade
cd /tmp/test-package-upgrade

# 初始化 Python 專案
python3 -m venv .venv
source .venv/bin/activate

# 安裝一個舊版本的套件
pip install requests==2.28.0

# 建立簡單的 Python 檔案使用 requests
cat > test_app.py <<'EOF'
import requests

def fetch_data(url):
    response = requests.get(url)
    return response.json()

if __name__ == "__main__":
    data = fetch_data("https://api.github.com")
    print(data)
EOF

# 建立 requirements.txt
echo "requests==2.28.0" > requirements.txt

# 初始化 git
git init
git add .
git commit -m "Initial commit"
```

### 測試 Skill

```bash
# 在測試專案中啟動 Claude Code
claude

# 然後輸入 (Dry Run):
檢查 requests 套件能不能從 2.28.0 升級到 2.32.0
```

Claude Code 應該會:
1. ✅ 偵測到使用 pip
2. ✅ 分析 requests 的依賴
3. ✅ (如果能連到 GitHub) 分析 breaking changes
4. ✅ 掃描 test_app.py 中的 requests 使用
5. ✅ 提供分析報告

**不要讓它真的執行升級!** 這只是測試 Skill 是否能正常運作。

---

## 驗證檢查清單

使用以下檢查清單確認安裝完成:

- [ ] `~/.claude/skills/package-upgrade/` 目錄存在
- [ ] `SKILL.md` 存在且 frontmatter 正確
- [ ] `README.md` 和 `LICENSE` 存在
- [ ] `scripts/` 目錄包含 7 個檔案
- [ ] `references/` 目錄包含 4 個 .md 檔案
- [ ] `templates/` 目錄包含 1 個 .md 檔案
- [ ] 所有 `.sh` 檔案有執行權限 (`-rwxr-xr-x`)
- [ ] 所有 `.py` 檔案有執行權限
- [ ] Python scripts 有正確的 shebang
- [ ] `pipdeptree` 已安裝
- [ ] `requests` Python 套件已安裝
- [ ] `jq` 命令可用
- [ ] Claude Code 可以列出 package-upgrade skill
- [ ] 測試專案中可以觸發 skill

全部打勾即安裝成功! ✅
