# 快速上手指南

## 🎯 3 分鐘安裝並開始使用

### 步驟 1: 安裝 (1 分鐘)

```bash
# 執行安裝腳本
bash install.sh
```

輸入 `y` 確認安裝。腳本會自動:
- ✅ 複製 skill 到 `~/.claude/skills/package-upgrade/`
- ✅ 設定執行權限
- ✅ 檢查並安裝依賴 (pipdeptree, requests)

---

### 步驟 2: 驗證 (1 分鐘)

```bash
# 執行驗證腳本
bash verify_installation.sh
```

**預期輸出**:
```
==========================================
Package Upgrade Skill 安裝驗證
==========================================

1. 檢查 Skill 目錄...
✓ Skill 目錄存在

2. 檢查核心檔案...
✓ LICENSE 存在
✓ README.md 存在
✓ SKILL.md 存在

...

==========================================
驗證結果總結
==========================================
通過: 28
失敗: 0

✓ 安裝驗證通過!
```

---

### 步驟 3: 開始使用 (1 分鐘)

```bash
# 啟動 Claude Code
claude
```

然後輸入以下任一指令:

#### 範例 1: 檢查可升級性
```
檢查 requests 能不能升級到 2.32.0
```

#### 範例 2: 執行升級
```
升級 requests 到 2.32.0
```

#### 範例 3: 修復 CVE
```
修復 CVE-2024-35195
```

---

## 📖 重要提醒

### ⚠️ Pip Lock 檔案

如果你的專案使用 pip 並且有 lock 檔案 (如 `requirements.lock`),
Skill 會**詢問你**如何產生 lock 檔案:

```
📋 偵測到專案使用 lock 檔案: requirements.lock

請選擇 lock 檔案產生方式:

[1] 使用 pip freeze (標準方式)
[2] 使用專案自定義腳本 (請告訴我命令)
[3] 我會手動處理,請繼續下一步
```

**常見情況**:
- **pip-tools**: 會自動執行 `pip-compile`
- **自定義 lock**: 會詢問你的產生方式
- **無 lock**: 直接更新 `requirements.txt`

詳見: `package-upgrade/references/PIP_LOCK_PATTERNS.md`

### ⚠️ Poetry / UV

**重要**: 必須使用正確的命令:

```bash
# ❌ 錯誤 - 只更新 lock
poetry update requests
uv lock --upgrade-package requests

# ✅ 正確 - 同時更新 pyproject.toml 和 lock
poetry add requests@2.32.0
uv add "requests>=2.32.0"
```

詳見: `package-upgrade/QUICK_REFERENCE.md`

---

## 🎨 使用者確認點

Skill 會在以下時間點暫停並等待你確認:

1. **依賴衝突** - 提供多種解決方案供選擇
2. **Pip Lock 檔案** - 詢問如何產生 lock
3. **程式碼修改** - 展示完整 diff 等待確認
4. **建立分支** - 告知分支名稱
5. **測試程式修改** - 解釋為什麼要改測試
6. **建立 PR** - 展示 PR 內容

你可以在任何時候:
- ✅ 同意繼續
- ✏️ 要求修改
- ⏸️ 暫停手動介入
- ❌ 中止並回退

---

## 📚 完整文件導航

### 安裝相關
- `README.md` - 本檔案,專案總覽
- `INSTALLATION_GUIDE.md` - 詳細安裝指南
- `VERIFICATION_CHECKLIST.md` - 完整驗證檢查清單
- `install.sh` - 自動安裝腳本
- `verify_installation.sh` - 自動驗證腳本

### 使用相關
- `package-upgrade/README.md` - Skill 使用說明
- `package-upgrade/SKILL.md` - 完整工作流程 (Phase 0-7)
- `package-upgrade/QUICK_REFERENCE.md` - 快速參考卡片

### 參考文件
- `package-upgrade/references/pip_workflow.md` - Pip 操作指南
- `package-upgrade/references/poetry_workflow.md` - Poetry 操作指南
- `package-upgrade/references/uv_workflow.md` - UV 操作指南
- `package-upgrade/references/PIP_LOCK_PATTERNS.md` - Pip lock 模式指南
- `package-upgrade/references/IMPORTANT_DEPENDENCY_UPDATE.md` - 依賴更新規則
- `package-upgrade/references/breaking_change_patterns.md` - Breaking change 識別

### 架構設計
- `package-upgrade-agent-architecture.md` - 完整架構設計文件
- `CHANGELOG.md` - 版本更新記錄

---

## 🆘 需要幫助?

### 問題排查順序

1. **檢查安裝**: `bash verify_installation.sh`
2. **查看文件**: `INSTALLATION_GUIDE.md` → 故障排除章節
3. **檢查權限**: `chmod +x ~/.claude/skills/package-upgrade/scripts/*`
4. **重新安裝**: `bash install.sh`

### 快速診斷

```bash
# 檢查 Skill 目錄
ls ~/.claude/skills/package-upgrade/SKILL.md

# 檢查依賴
python3 -c "import pipdeptree, requests"

# 檢查工具
jq --version
git --version
```

---

## 🎊 安裝成功後

你現在可以:

1. ✅ 自動升級 Python 套件
2. ✅ 自動分析 breaking changes
3. ✅ 自動修改受影響的程式碼
4. ✅ 自動執行測試並診斷失敗
5. ✅ 自動產生遷移報告和 PR
6. ✅ 修復 CVE 漏洞

**開始你的第一次升級**:
```bash
claude "升級 requests 到 2.32.0"
```

享受自動化的套件升級體驗! 🚀
