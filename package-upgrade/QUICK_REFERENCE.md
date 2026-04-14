# 快速參考卡片

## 🎯 正確的套件升級命令

### pip

#### 有 pip-tools (requirements.in)
```bash
# 1. 編輯 requirements.in
vim requirements.in  # requests==2.28.0 → requests==2.32.0

# 2. 重新編譯
pip-compile requirements.in

# 3. 安裝
pip-sync requirements.txt
```

#### 有 lock 檔案 (requirements.lock)
```bash
# 1. 編輯 requirements.txt
vim requirements.txt  # requests==2.28.0 → requests==2.32.0

# 2. 重新產生 lock
pip install -r requirements.txt
pip freeze > requirements.lock
```

#### 無 lock 檔案
```bash
# 1. 編輯 requirements.txt
vim requirements.txt  # requests==2.28.0 → requests==2.32.0

# 2. 安裝
pip install -r requirements.txt
```

### poetry
```bash
# 一個命令同時更新 pyproject.toml 和 poetry.lock
poetry add requests@2.32.0
```

### uv (專案模式)
```bash
# 一個命令同時更新 pyproject.toml 和 uv.lock
uv add "requests>=2.32.0"
```

---

## ❌ 常見錯誤

### 錯誤 1: Poetry 只更新 lock
```bash
❌ poetry update requests  # 不會改 pyproject.toml
❌ poetry lock             # 不會改 pyproject.toml

✅ poetry add requests@2.32.0  # 同時更新兩者
```

### 錯誤 2: UV 只更新 lock
```bash
❌ uv lock --upgrade-package requests  # 不會改 pyproject.toml

✅ uv add "requests>=2.32.0"  # 同時更新兩者
```

### 錯誤 3: Pip 只安裝不更新檔案
```bash
❌ pip install --upgrade requests==2.32.0  # 不會寫入任何檔案

✅ 先編輯 requirements.txt (或 .in),再執行對應命令
```

### 錯誤 4: Pip 編輯錯誤的檔案
```bash
❌ vim requirements.txt  # 如果這是 pip-tools 的 lock 檔案!

✅ 檢查是否有 requirements.in,有的話編輯 .in 檔案
```

### 錯誤 5: Pip 有 lock 但沒更新
```bash
❌ vim requirements.txt && pip install -r requirements.txt
   # 忘記更新 requirements.lock!

✅ 同時更新 requirements.txt 和 requirements.lock
```

---

## 📋 驗證更新

### pip

#### pip-tools 模式
```bash
# 檢查 requirements.in (約束檔案)
grep "requests" requirements.in
# 應該: requests==2.32.0

# 檢查 requirements.txt (lock 檔案)
grep "requests" requirements.txt
# 應該: requests==2.32.0 (加上所有子依賴)
```

#### 有 lock 檔案
```bash
# 檢查 requirements.txt
grep "requests" requirements.txt
# 應該: requests==2.32.0

# 檢查 lock 檔案
grep "requests" requirements.lock
# 應該: requests==2.32.0 (加上所有子依賴)
```

#### 無 lock 檔案
```bash
grep "requests" requirements.txt
# 應該: requests==2.32.0
```

### poetry
```bash
# 檢查 pyproject.toml
grep "requests" pyproject.toml
# 應該: requests = "^2.32.0"

# 檢查 poetry.lock
poetry show requests
# 應該: version : 2.32.0
```

### uv
```bash
# 檢查 pyproject.toml
grep "requests" pyproject.toml
# 應該在 dependencies: "requests>=2.32.0"

# 檢查安裝版本
uv pip list | grep requests
# 應該: requests 2.32.0
```

---

## 🔍 快速診斷

### 症狀: Lock 檔案有新版本,但 pyproject.toml 是舊版本

**原因**: 使用了錯誤的命令

**修復**:
```bash
# Poetry
poetry add <package>@<version>

# UV
uv add "<package>>=<version>"

# 然後 commit 兩個檔案
git add pyproject.toml poetry.lock  # 或 uv.lock
git commit -m "upgrade package to version"
```

---

## 📚 詳細文件

- **IMPORTANT_DEPENDENCY_UPDATE.md** - 完整說明與對比表
- **pip_workflow.md** - Pip 詳細操作指南
- **poetry_workflow.md** - Poetry 詳細操作指南
- **uv_workflow.md** - UV 詳細操作指南
