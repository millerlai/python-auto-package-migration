# 安裝驗證檢查清單

## 🚀 快速驗證 (3 步驟)

### 1️⃣ 自動驗證
```bash
bash verify_installation.sh
```

### 2️⃣ 檢查目錄
```bash
ls ~/.claude/skills/package-upgrade/
```
應該看到: LICENSE, README.md, SKILL.md, scripts/, references/, templates/

### 3️⃣ Claude Code 測試
```bash
claude
```
然後輸入: `list available skills`

---

## 📋 完整檢查清單

### ✅ 檔案結構檢查

- [ ] **核心檔案** (3 個)
  ```bash
  ls ~/.claude/skills/package-upgrade/{LICENSE,README.md,SKILL.md}
  ```

- [ ] **Scripts 目錄** (7 個檔案)
  ```bash
  ls ~/.claude/skills/package-upgrade/scripts/
  ```
  應該有:
  - detect_env.sh
  - dep_tree.py
  - ast_scanner.py
  - fetch_changelog.py
  - git_diff.sh
  - run_tests.sh
  - snapshot_env.sh

- [ ] **References 目錄** (5 個檔案)
  ```bash
  ls ~/.claude/skills/package-upgrade/references/
  ```
  應該有:
  - pip_workflow.md
  - poetry_workflow.md
  - uv_workflow.md
  - breaking_change_patterns.md
  - IMPORTANT_DEPENDENCY_UPDATE.md
  - PIP_LOCK_PATTERNS.md

- [ ] **Templates 目錄** (1 個檔案)
  ```bash
  ls ~/.claude/skills/package-upgrade/templates/
  ```
  應該有: report_structure.md

### ✅ 執行權限檢查

- [ ] **Bash Scripts 可執行**
  ```bash
  ls -la ~/.claude/skills/package-upgrade/scripts/*.sh
  ```
  每個都應該是: `-rwxr-xr-x`

- [ ] **Python Scripts 可執行**
  ```bash
  ls -la ~/.claude/skills/package-upgrade/scripts/*.py
  ```
  每個都應該是: `-rwxr-xr-x`

### ✅ 內容格式檢查

- [ ] **SKILL.md Frontmatter**
  ```bash
  head -15 ~/.claude/skills/package-upgrade/SKILL.md
  ```
  應該看到:
  ```yaml
  ---
  name: package-upgrade
  description: >
    升級 Python 套件或修復 CVE 漏洞...
  ---
  ```

- [ ] **Python Scripts Shebang**
  ```bash
  head -1 ~/.claude/skills/package-upgrade/scripts/*.py
  ```
  每個都應該是: `#!/usr/bin/env python3`

- [ ] **Bash Scripts Shebang**
  ```bash
  head -1 ~/.claude/skills/package-upgrade/scripts/*.sh
  ```
  每個都應該是: `#!/usr/bin/env bash`

### ✅ 依賴檢查

- [ ] **Python 3.8+**
  ```bash
  python3 --version
  ```
  應該 ≥ 3.8

- [ ] **pipdeptree**
  ```bash
  pipdeptree --version
  ```
  或
  ```bash
  python3 -c "import pipdeptree"
  ```

- [ ] **requests**
  ```bash
  python3 -c "import requests; print(requests.__version__)"
  ```

- [ ] **git**
  ```bash
  git --version
  ```

- [ ] **jq**
  ```bash
  jq --version
  ```

- [ ] **gh (可選)**
  ```bash
  gh --version
  ```

### ✅ 功能測試

- [ ] **detect_env.sh**
  ```bash
  bash ~/.claude/skills/package-upgrade/scripts/detect_env.sh .
  ```
  應該輸出 JSON

- [ ] **dep_tree.py** (如果專案有 requests)
  ```bash
  python3 ~/.claude/skills/package-upgrade/scripts/dep_tree.py . requests
  ```
  應該輸出 JSON

- [ ] **ast_scanner.py** (如果專案有 requests)
  ```bash
  python3 ~/.claude/skills/package-upgrade/scripts/ast_scanner.py . requests
  ```
  應該輸出 JSON

### ✅ Claude Code 整合

- [ ] **Skill 被識別**
  
  在 Claude Code 中輸入:
  ```
  list available skills
  ```
  應該看到 `package-upgrade` 出現

- [ ] **Skill 資訊正確**
  
  在 Claude Code 中輸入:
  ```
  show me the package-upgrade skill
  ```
  應該顯示 skill 的描述

- [ ] **可以觸發** (Dry Run)
  
  在 Claude Code 中輸入:
  ```
  檢查這個專案能不能升級 requests
  ```
  應該開始執行 Phase 0 環境偵測

---

## 🎯 快速驗證命令

一次執行所有檢查:

```bash
# 自動驗證
bash verify_installation.sh && echo "" && \
echo "✅ 驗證通過! 請繼續在 Claude Code 中測試:" && \
echo "" && \
echo "  claude" && \
echo "  # 然後輸入: list available skills"
```

---

## ❌ 常見失敗與修復

### 失敗: 目錄不存在
```bash
# 重新安裝
bash install.sh
```

### 失敗: 權限錯誤
```bash
chmod +x ~/.claude/skills/package-upgrade/scripts/*.sh
chmod +x ~/.claude/skills/package-upgrade/scripts/*.py
```

### 失敗: 缺少依賴
```bash
pip install pipdeptree requests
brew install jq  # macOS
```

### 失敗: Claude Code 看不到 Skill
```bash
# 檢查 frontmatter
head -15 ~/.claude/skills/package-upgrade/SKILL.md

# 重啟 Claude Code
```

---

## 📊 驗證結果解讀

### ✅ 完全通過 (28/28)
```
✓ 安裝驗證通過!
```
→ 可以開始使用

### ⚠️ 部分警告
```
通過: 25
失敗: 0
⚠ jq 不可用
⚠ gh CLI 不可用
```
→ 基本功能可用,建議安裝 jq

### ❌ 有失敗
```
通過: 20
失敗: 3
✗ pipdeptree 未安裝
```
→ 必須修復失敗項目

---

## 🧪 測試專案建立

用於完整功能測試:

```bash
# 建立測試專案
mkdir -p /tmp/test-package-upgrade
cd /tmp/test-package-upgrade

# 初始化
python3 -m venv .venv
source .venv/bin/activate

# 安裝舊版本套件
pip install requests==2.28.0
echo "requests==2.28.0" > requirements.txt

# 建立測試程式
cat > app.py <<'EOF'
import requests

def fetch_data(url):
    response = requests.get(url)
    return response.json()
EOF

# Git 初始化
git init
git add .
git commit -m "Initial commit"

# 測試 Skill
claude
# 輸入: 檢查 requests 能不能升級到 2.32.0
```

---

## ✨ 驗證通過後的下一步

1. **閱讀文件**
   - `package-upgrade/README.md` - 使用說明
   - `package-upgrade/QUICK_REFERENCE.md` - 快速參考

2. **了解工作流程**
   - `package-upgrade/SKILL.md` - Phase 0-7 完整流程

3. **開始使用**
   ```
   claude "升級 requests 到 2.32.0"
   ```

4. **查看範例**
   - CVE 修復範例
   - 依賴衝突處理範例

---

全部檢查完成後,你就可以放心使用這個 Skill 了! 🎊
