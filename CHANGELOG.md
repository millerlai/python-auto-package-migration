# Changelog

## [Unreleased]

### Fixed
- **重要修正**: 修正 poetry 和 uv 套件管理工具只更新鎖定檔案,沒有更新 `pyproject.toml` 的問題
  - 更新 `poetry_workflow.md` 說明必須使用 `poetry add` 而非 `poetry update`
  - 更新 `uv_workflow.md` 說明必須使用 `uv add` 而非 `uv lock --upgrade-package`
  - 更新 `pip_workflow.md` 強調 pip 不會自動寫入任何檔案
  - 在 `SKILL.md` Phase 5.3 中詳細說明正確的更新流程
  - 新增 `IMPORTANT_DEPENDENCY_UPDATE.md` 文件,詳細說明各工具的正確使用方式

- **重要修正**: 加入 pip lock 檔案檢測與處理
  - 更新 `detect_env.sh` 自動檢測 pip-tools (requirements.in) 和自定義 lock 檔案
  - 新增 `pip_lock_file` 和 `has_pip_tools` 欄位到環境偵測輸出
  - 在 `SKILL.md` Phase 0 中說明 pip lock 檔案的檢測
  - 在 `SKILL.md` Phase 5.3 中加入 pip lock 檔案的處理流程,會詢問使用者確認
  - 支援常見的 lock 檔案模式: `requirements.lock`, `requirements.txt.lock`, `requirements-lock.txt` 等

### Changed
- **架構調整**: 移除 symlink 設計,Python scripts 直接放在 `package-upgrade/scripts/` 目錄
  - 簡化安裝流程,不需要保留 src/ 目錄
  - 使用者已將 src/*.py 直接搬移到 scripts/ 目錄
  - 移除 verify_installation.sh 中的 symlink 檢查
  - 更新所有文件移除 symlink 相關說明
  - 更新 README.md 目錄結構說明,移除 src/ 目錄
  - 更新 INSTALLATION_GUIDE.md 移除 symlink 驗證步驟

- **專案套件管理**: 將專案本身改用 UV 管理
  - 新增 `pyproject.toml` 使用 UV 格式配置
  - 新增 `uv.lock` 鎖定檔案
  - 使用 `dependency-groups` 管理開發依賴
  - 配置 hatchling 作為 build backend
  - 虛擬環境在 `.venv/` (已在 .gitignore)

### Added
- 新增 `IMPORTANT_DEPENDENCY_UPDATE.md` - 依賴檔案更新規則總覽
- 新增 `QUICK_REFERENCE.md` - 快速參考卡片
- 新增 `PIP_LOCK_PATTERNS.md` - Pip lock 檔案模式完整指南
- 新增 `VERIFICATION_CHECKLIST.md` - 完整的安裝驗證檢查清單
- 新增 `GETTING_STARTED.md` - 3 分鐘快速上手指南
- 新增 `DEVELOPMENT.md` - 開發者指南 (UV 使用說明)
- 新增 `pyproject.toml` - UV 專案配置檔案
- 新增 `uv.lock` - UV 鎖定檔案
- 擴展 `detect_env.sh` 支援檢測多種 pip lock 檔案模式:
  - 檢測 pip-tools (requirements.in)
  - 檢測常見 lock 檔案 (requirements.lock, requirements.txt.lock 等)
  - 新增 `pip_lock_file` 和 `has_pip_tools` 輸出欄位
- 在 Phase 5.3 中加入使用者確認機制,詢問如何處理 pip lock 檔案
  - 情況 A: pip-tools → 自動執行 pip-compile
  - 情況 B: 自定義 lock → 詢問使用者產生方式
  - 情況 C: 無 lock → 直接編輯安裝

## [1.0.0] - 2026-04-14

### Added
- 初始版本發布
- 完整的 Claude Code Skill 實作
- 支援 pip、poetry、uv 三種套件管理工具
- 自動化 breaking changes 分析 (Changelog + Git Diff)
- AST 程式碼掃描與修改建議
- 測試失敗診斷 (三向交叉分析)
- Git 整合 (自動建立分支和 PR)
- 完整的遷移報告產出
- 安裝驗證腳本 (`verify_installation.sh`)
- 一鍵安裝腳本 (`install.sh`)
- 詳細的安裝指南 (`INSTALLATION_GUIDE.md`)
