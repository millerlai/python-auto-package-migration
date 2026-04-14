# 開發指南

## 專案套件管理

本專案使用 **UV** 作為套件管理工具。

### 安裝 UV

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# 或使用 brew (macOS)
brew install uv

# 或使用 pip
pip install uv
```

---

## 開發環境設定

### 初始設定

```bash
# Clone 專案
git clone https://github.com/YOUR_USERNAME/package-upgrade-skill.git
cd package-upgrade-skill

# 使用 uv 安裝所有依賴 (包含開發依賴)
uv sync

# 啟用虛擬環境 (可選)
source .venv/bin/activate
```

**`uv sync` 會自動**:
1. ✅ 建立虛擬環境 (`.venv/`)
2. ✅ 安裝主要依賴 (requests)
3. ✅ 安裝開發依賴 (pipdeptree, pytest, black, ruff, mypy)
4. ✅ 以 editable 模式安裝本專案

---

## 依賴管理

### 新增依賴

```bash
# 新增主要依賴
uv add <package>

# 範例
uv add click

# 新增開發依賴
uv add --dev <package>

# 範例
uv add --dev pytest-asyncio
```

### 更新依賴

```bash
# 更新所有依賴到最新版本
uv lock --upgrade

# 更新特定套件
uv lock --upgrade-package requests

# 同步安裝
uv sync
```

### 移除依賴

```bash
# 移除依賴
uv remove <package>

# 範例
uv remove click
```

---

## 執行 Scripts

### 使用 uv run (推薦)

```bash
# 直接執行 Python scripts (自動使用 .venv)
uv run python package-upgrade/scripts/dep_tree.py . requests

uv run python package-upgrade/scripts/ast_scanner.py . requests

uv run python package-upgrade/scripts/fetch_changelog.py requests https://github.com/psf/requests
```

### 或啟用虛擬環境

```bash
# 啟用 venv
source .venv/bin/activate

# 執行 scripts
python package-upgrade/scripts/dep_tree.py . requests

# 離開 venv
deactivate
```

---

## 測試

### 執行測試 (當測試檔案建立後)

```bash
# 執行所有測試
uv run pytest

# 執行特定測試
uv run pytest tests/test_ast_scanner.py

# 執行測試並顯示覆蓋率
uv run pytest --cov=package-upgrade --cov-report=html
```

---

## 程式碼品質

### 格式化

```bash
# 使用 black 格式化程式碼
uv run black package-upgrade/scripts/*.py

# 檢查格式
uv run black --check package-upgrade/scripts/*.py
```

### Linting

```bash
# 使用 ruff 檢查程式碼
uv run ruff check package-upgrade/scripts/*.py

# 自動修復
uv run ruff check --fix package-upgrade/scripts/*.py
```

### 型別檢查

```bash
# 使用 mypy 檢查型別
uv run mypy package-upgrade/scripts/*.py
```

---

## 修改 Scripts

### 工作流程

1. **修改 scripts**
   ```bash
   vim package-upgrade/scripts/dep_tree.py
   ```

2. **測試修改**
   ```bash
   uv run python package-upgrade/scripts/dep_tree.py . requests
   ```

3. **格式化與檢查**
   ```bash
   uv run black package-upgrade/scripts/dep_tree.py
   uv run ruff check package-upgrade/scripts/dep_tree.py
   ```

4. **提交變更**
   ```bash
   git add package-upgrade/scripts/dep_tree.py
   git commit -m "feat: improve dep_tree.py error handling"
   ```

---

## 安裝測試

### 測試安裝流程

```bash
# 執行安裝腳本
bash install.sh

# 驗證安裝
bash verify_installation.sh

# 測試 Skill (建立測試專案)
mkdir -p /tmp/test-skill
cd /tmp/test-skill
python3 -m venv .venv
source .venv/bin/activate
pip install requests==2.28.0
echo "requests==2.28.0" > requirements.txt

# 測試
claude "檢查 requests 能不能升級到 2.32.0"
```

---

## 發布準備

### 檢查清單

- [ ] 所有 scripts 都有執行權限
  ```bash
  chmod +x package-upgrade/scripts/*.sh
  chmod +x package-upgrade/scripts/*.py
  ```

- [ ] 所有 scripts 都有正確的 shebang
  ```bash
  head -1 package-upgrade/scripts/*.py  # #!/usr/bin/env python3
  head -1 package-upgrade/scripts/*.sh  # #!/usr/bin/env bash
  ```

- [ ] 更新版本號
  ```bash
  # 更新 pyproject.toml 中的 version
  # 更新 CHANGELOG.md
  ```

- [ ] 執行完整驗證
  ```bash
  bash verify_installation.sh
  ```

- [ ] 測試安裝腳本
  ```bash
  bash install.sh
  ```

---

## 專案結構

```
package-upgrade-skill/
├── pyproject.toml           # UV 專案配置 ⭐
├── uv.lock                  # UV 鎖定檔案 ⭐
├── .venv/                   # 虛擬環境 (不 commit)
│
├── package-upgrade/         # Skill 目錄 (發布單位)
│   ├── scripts/             # 所有 Python scripts 在此
│   │   ├── dep_tree.py
│   │   ├── ast_scanner.py
│   │   └── fetch_changelog.py
│   ├── references/
│   └── templates/
│
├── install.sh               # 安裝腳本
├── verify_installation.sh   # 驗證腳本
└── README.md                # 專案說明
```

**注意**: 
- ✅ Python scripts 直接在 `package-upgrade/scripts/`
- ✅ 不使用 `src/` 目錄
- ✅ 不使用 symlinks

---

## UV 常用命令

### 依賴管理

```bash
# 安裝所有依賴
uv sync

# 只安裝主要依賴 (不含 dev)
uv sync --no-dev

# 新增套件
uv add requests

# 新增開發套件
uv add --dev pytest

# 移除套件
uv remove requests

# 更新套件
uv lock --upgrade-package requests
uv sync
```

### 執行命令

```bash
# 執行 Python 腳本
uv run python script.py

# 執行測試
uv run pytest

# 執行格式化
uv run black .

# 執行 linting
uv run ruff check .
```

### 環境管理

```bash
# 查看環境資訊
uv pip list

# 查看已安裝套件
uv pip show requests

# 查看依賴樹
uv pip tree

# 清理環境
rm -rf .venv
uv sync  # 重新建立
```

---

## 貢獻流程

1. **Fork 專案**

2. **Clone 並設定環境**
   ```bash
   git clone https://github.com/YOUR_USERNAME/package-upgrade-skill.git
   cd package-upgrade-skill
   uv sync
   ```

3. **建立 feature branch**
   ```bash
   git checkout -b feature/your-feature
   ```

4. **開發並測試**
   ```bash
   # 修改程式碼
   vim package-upgrade/scripts/your_script.py
   
   # 格式化
   uv run black package-upgrade/scripts/your_script.py
   
   # 檢查
   uv run ruff check package-upgrade/scripts/your_script.py
   
   # 測試
   uv run python package-upgrade/scripts/your_script.py test_args
   ```

5. **Commit 變更**
   ```bash
   git add .
   git commit -m "feat: add new feature"
   ```

6. **Push 並建立 PR**
   ```bash
   git push origin feature/your-feature
   gh pr create
   ```

---

## 故障排除

### Q: uv sync 失敗

**檢查**:
```bash
# 檢查 uv 版本
uv --version

# 檢查 pyproject.toml 格式
uv check pyproject.toml
```

### Q: 缺少依賴

**解決**:
```bash
# 重新同步
uv sync --reinstall
```

### Q: 虛擬環境損壞

**解決**:
```bash
# 刪除並重建
rm -rf .venv
uv sync
```

---

## UV vs Poetry/Pip

| 操作 | pip | poetry | uv |
|------|-----|--------|-----|
| 安裝依賴 | `pip install -r req.txt` | `poetry install` | `uv sync` |
| 新增套件 | 編輯檔案 + `pip install` | `poetry add pkg` | `uv add pkg` |
| 更新套件 | 編輯檔案 + `pip install` | `poetry add pkg@ver` | `uv add pkg` |
| 移除套件 | 編輯檔案 + `pip uninstall` | `poetry remove pkg` | `uv remove pkg` |
| 執行腳本 | `python script.py` | `poetry run python script.py` | `uv run python script.py` |
| 速度 | 慢 | 中 | 極快 (10-100x) |

---

## 參考資源

- [UV 官方文件](https://docs.astral.sh/uv/)
- [UV GitHub](https://github.com/astral-sh/uv)
- [Python Packaging Guide](https://packaging.python.org/)
