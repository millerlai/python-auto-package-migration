# Package Upgrade Skill for Claude Code

這是一個基於 Claude Code 的智能 Python 套件升級助手,能夠自動化分析、修改程式碼、執行測試,並產出完整的遷移報告。

## 🚀 快速開始

### 一鍵安裝

```bash
# 全域安裝 (推薦 - 所有專案可用)
bash install.sh

# 或專案級安裝 (僅此專案可用)
bash install.sh --project
```

### 驗證安裝

```bash
bash verify_installation.sh
```

**預期輸出**:
```
✓ 安裝驗證通過!
通過: 28
失敗: 0
```

詳細檢查清單請參考: `VERIFICATION_CHECKLIST.md`

### 立即使用

```bash
claude "升級 requests 到 2.32.0"
```

---

## ✨ 功能特色

- 🔍 **智能分析**: 自動從 Changelog + Git Diff 雙重來源分析 breaking changes
- 🛠️ **自動修改**: 理解程式碼上下文,生成符合專案風格的修改
- ✅ **測試診斷**: 三向交叉分析測試失敗原因 (業務碼/測試碼/配置)
- 📝 **完整報告**: 產出專業的遷移報告和 Pull Request
- 🔒 **CVE 修復**: 自動評估漏洞風險並提供修復方案
- 🎯 **多工具支援**: pip、poetry、uv 三種套件管理工具

---

## 📋 目錄結構

```
python-auto-package-mgiration/
├── README.md                          # 本檔案
├── GETTING_STARTED.md                 # 3 分鐘快速上手
├── INSTALLATION_GUIDE.md              # 詳細安裝指南
├── VERIFICATION_CHECKLIST.md          # 驗證檢查清單
├── DEVELOPMENT.md                     # 開發指南 ⭐
├── CHANGELOG.md                       # 版本更新記錄
├── install.sh                         # 一鍵安裝腳本
├── verify_installation.sh             # 安裝驗證腳本
│
├── pyproject.toml                     # UV 專案配置 ⭐
├── uv.lock                            # UV 鎖定檔案 ⭐
├── .venv/                             # 虛擬環境 (不 commit)
├── .gitignore                         # Git 忽略檔案
│
├── package-upgrade/                   # Claude Code Skill (複製到 ~/.claude/skills/)
│   ├── README.md                      # Skill 使用說明
│   ├── SKILL.md                       # 主技能定義
│   ├── QUICK_REFERENCE.md             # 快速參考卡片
│   ├── LICENSE                        # MIT 授權
│   ├── scripts/                       # Helper scripts (所有 .sh 和 .py)
│   │   ├── detect_env.sh              # 環境偵測 (支援 pip lock)
│   │   ├── dep_tree.py                # 依賴樹分析器
│   │   ├── ast_scanner.py             # AST 程式碼掃描器
│   │   ├── fetch_changelog.py         # Changelog 抓取器
│   │   ├── git_diff.sh                # Git diff 生成
│   │   ├── run_tests.sh               # 測試執行
│   │   └── snapshot_env.sh            # 環境備份/回退
│   ├── references/                    # 參考文件 (6 個)
│   │   ├── pip_workflow.md            # Pip 操作指南
│   │   ├── poetry_workflow.md         # Poetry 操作指南
│   │   ├── uv_workflow.md             # UV 操作指南
│   │   ├── breaking_change_patterns.md # Breaking change 識別
│   │   ├── IMPORTANT_DEPENDENCY_UPDATE.md # 依賴更新規則 ⭐
│   │   └── PIP_LOCK_PATTERNS.md       # Pip lock 模式 ⭐
│   └── templates/
│       └── report_structure.md        # 報告撰寫指南
│
└── package-upgrade-agent-architecture.md  # 完整架構設計文件
```

**本專案使用 UV 管理依賴** - 詳見 `DEVELOPMENT.md`

---

## 🔧 手動安裝

如果不想用自動安裝腳本,可以手動執行:

### 1. 複製 Skill

```bash
# 全域安裝
cp -r package-upgrade ~/.claude/skills/

# 或專案級安裝
mkdir -p .claude/skills/
cp -r package-upgrade .claude/skills/
```

### 2. 設定執行權限

```bash
chmod +x ~/.claude/skills/package-upgrade/scripts/*.sh
chmod +x ~/.claude/skills/package-upgrade/scripts/*.py
```

### 3. 安裝依賴

```bash
# Python 依賴
pip install pipdeptree requests

# 系統工具 (macOS)
brew install jq

# 系統工具 (Ubuntu/Debian)
sudo apt-get install jq
```

### 4. 驗證安裝

```bash
bash verify_installation.sh
```

---

## ✅ 驗證步驟

### 自動驗證 (推薦)

```bash
bash verify_installation.sh
```

驗證腳本會檢查:
- ✅ Skill 目錄是否存在
- ✅ 所有必要檔案是否存在
- ✅ Scripts 是否有執行權限
- ✅ Python scripts 格式是否正確
- ✅ Python 依賴是否安裝
- ✅ SKILL.md frontmatter 是否正確
- ✅ 功能測試

### 手動驗證

#### 檢查檔案結構

```bash
ls -la ~/.claude/skills/package-upgrade/
```

應該看到:
- LICENSE
- README.md
- SKILL.md
- scripts/ (7 個檔案)
- references/ (4 個檔案)
- templates/ (1 個檔案)

#### 檢查執行權限

```bash
ls -la ~/.claude/skills/package-upgrade/scripts/
```

所有 `.sh` 和 `.py` 檔案應該有 `x` 權限 (例: `-rwxr-xr-x`)

#### 測試 Helper Scripts

```bash
# 測試環境偵測
bash ~/.claude/skills/package-upgrade/scripts/detect_env.sh .

# 應該輸出 JSON:
# {
#   "pkg_manager": "pip",
#   "python_version": "3.11.4",
#   ...
# }
```

#### 在 Claude Code 中驗證

```bash
claude
```

然後輸入:
```
list available skills
```

或
```
show me the package-upgrade skill
```

應該會看到 `package-upgrade` 出現在列表中。

---

## 📖 使用範例

### 基本升級

```bash
claude "升級 requests 到 2.32.0"
```

### CVE 修復

```bash
claude "修復 CVE-2024-35195"
```

### 檢查可行性

```bash
claude "檢查 django 能不能從 4.2 升到 5.1"
```

### 依賴衝突處理

當遇到依賴衝突時,Skill 會:
1. 分析衝突原因
2. 提出多種解決方案
3. 評估每個方案的風險
4. 等待你選擇方案

---

## 🎯 核心工作流程

1. **Phase 0: 環境偵測** - 自動識別 pip/poetry/uv
2. **Phase 1: 輸入解析** - 解析 package 名稱或 CVE 編號
3. **Phase 2: 依賴分析** - 分析依賴樹,識別衝突
4. **Phase 3: Breaking Change 分析** - Changelog + Git Diff 雙軌分析
5. **Phase 4: 程式碼影響分析** - AST 掃描 + 修改建議
6. **Phase 5: 執行升級** - 建立 Git branch → 備份 → 修改
7. **Phase 6: 測試驗證** - 分層測試 + 三向診斷
8. **Phase 7: 產出報告** - 遷移報告 + Commit + PR

詳見: `package-upgrade/SKILL.md`

---

## 📚 文件

- **INSTALLATION_GUIDE.md** - 詳細安裝與驗證指南
- **package-upgrade/README.md** - Skill 使用說明
- **package-upgrade/SKILL.md** - 完整工作流程定義
- **package-upgrade-agent-architecture.md** - 架構設計文件

---

## 🔍 故障排除

### Skill 找不到

```bash
# 檢查安裝路徑
ls ~/.claude/skills/package-upgrade/SKILL.md

# 如果不存在,重新安裝
bash install.sh
```

### Permission denied

```bash
chmod +x ~/.claude/skills/package-upgrade/scripts/*.sh
chmod +x ~/.claude/skills/package-upgrade/scripts/*.py
```

### 缺少依賴

```bash
pip install pipdeptree requests
brew install jq  # macOS
```

更多問題請參考 `INSTALLATION_GUIDE.md` 的故障排除章節。

---

## 🧪 測試安裝

建立測試專案來驗證 Skill:

```bash
# 建立測試專案
mkdir -p /tmp/test-skill
cd /tmp/test-skill

# 初始化
python3 -m venv .venv
source .venv/bin/activate
pip install requests==2.28.0
echo "requests==2.28.0" > requirements.txt

# 建立測試程式
cat > app.py <<EOF
import requests

def fetch_data(url):
    return requests.get(url).json()
EOF

# 初始化 git
git init
git add .
git commit -m "Initial commit"

# 測試 Skill (Dry Run)
claude "檢查 requests 能不能從 2.28.0 升級到 2.32.0"
```

**不要真的執行升級!** 這只是測試 Skill 是否正常運作。

---

## 🛠️ 開發

### 本專案使用 UV 管理依賴

```bash
# Clone 專案
git clone https://github.com/YOUR_USERNAME/package-upgrade-skill.git
cd package-upgrade-skill

# 安裝 UV (如果還沒安裝)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 安裝所有依賴 (包含開發依賴)
uv sync

# 執行 scripts
uv run python package-upgrade/scripts/dep_tree.py . requests

# 格式化程式碼
uv run black package-upgrade/scripts/

# Lint 檢查
uv run ruff check package-upgrade/scripts/
```

詳細開發指南請參考: `DEVELOPMENT.md`

---

## 🤝 貢獻

歡迎貢獻!

### 貢獻方向
- 支援更多套件管理工具 (conda / pipenv)
- 支援其他語言 (Node.js / Ruby / Go)
- 改進 breaking change 偵測
- 增加測試框架支援
- 改進錯誤診斷邏輯

---

## 📄 授權

MIT License - 詳見 `package-upgrade/LICENSE`

---

## 🙏 致謝

- [Claude Code](https://claude.ai/code) by Anthropic
- [pipdeptree](https://github.com/tox-dev/pipdeptree)
- [poetry](https://python-poetry.org/)
- [uv](https://github.com/astral-sh/uv)

---

## 📞 聯絡

如有問題或建議,請開 Issue 或 Discussion。
