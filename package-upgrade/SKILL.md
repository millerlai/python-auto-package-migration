---
name: package-upgrade
description: >
  升級 Python 套件或修復 CVE 漏洞的完整工作流。當使用者提到
  「升級 package」、「更新套件」、「fix CVE」、「修復漏洞」、
  「package migration」、「dependency update」、「bump version」
  時觸發此 skill。也適用於使用者提供 CVE 編號 (如 CVE-2024-xxxxx)
  並希望修復的場景。支援 pip、poetry、uv 三種套件管理工具，
  自動偵測專案使用的工具。即使使用者只是隨口問「這個套件能不能升級」，
  也應觸發此 skill 來做完整分析。
---

# Package Upgrade / CVE Fix Skill

## 概觀

你是一位資深的 Python 套件遷移專家。當使用者要求升級套件或修復 CVE 時，
按照以下工作流程逐步執行。你自己就是分析引擎 — 不需要呼叫外部 LLM API。

關鍵原則:
- **在修改任何專案內容之前，必須先建立新的 Git 分支** (Phase 5.1)
- 每個步驟先用 helper script 取得結構化數據，再用你的推理能力分析
- 在修改任何檔案之前，先備份環境
- 測試程式的修改必須經過使用者確認
- 完成後建立 Pull Request 供 review
- 全程保持可回退

---

## Phase 0: 環境偵測

執行 helper script 偵測專案環境:

```bash
bash scripts/detect_env.sh <project_path>
```

輸出為 JSON，包含:
- `pkg_manager`: pip | poetry | uv
- `python_version`: 例 3.11.4
- `lockfile_path`: 鎖定檔路徑 (如有)
- `pip_lock_file`: pip 專案的 lock 檔案 (如 requirements.lock)
- `has_pip_tools`: 是否使用 pip-tools (requirements.in)
- `dependency_files`: 依賴宣告檔清單

根據偵測到的 pkg_manager，讀取對應的 references 文件:
- pip → 讀 `references/pip_workflow.md`
- poetry → 讀 `references/poetry_workflow.md`
- uv → 讀 `references/uv_workflow.md`

**特別注意 pip 專案的 lock 檔案**:

如果偵測到 `pip_lock_file` 不為空,表示專案使用了 lock 機制:
- `requirements.in` + `requirements.txt` → 使用 pip-tools
- `requirements.txt` + `requirements.lock` → 使用自定義 lock
- `requirements.txt.lock` 或其他 `*.lock` → 自定義 lock 模式

**⚠️ 重要**: 在開始前,先閱讀 `references/IMPORTANT_DEPENDENCY_UPDATE.md`,
了解如何正確更新依賴檔案。關鍵要點:
- **pip**: 必須手動編輯 `requirements.txt` 或 `pyproject.toml`
- **poetry**: 使用 `poetry add pkg@version` (不是 `poetry update`)
- **uv**: 使用 `uv add "pkg>=version"` (不是 `uv lock --upgrade-package`)

---

## Phase 1: 輸入解析

### 情況 A: 使用者指定 package 名稱

直接進入 Phase 2。

### 情況 B: 使用者提供 CVE 編號

1. 用 web search 查詢 CVE 資訊:
   - 搜尋 `{CVE-ID} python package fix`
   - 搜尋 `site:osv.dev {CVE-ID}`
   - 搜尋 `site:nvd.nist.gov {CVE-ID}`

2. 從搜尋結果中提取:
   - 受影響的 package 名稱
   - 受影響的版本範圍
   - 修復版本
   - 嚴重性 (CVSS)
   - 漏洞描述

3. **你的分析任務** (這是你作為 LLM 的價值):
   - 閱讀 CVE 描述，理解漏洞的攻擊向量
   - 用 `grep -rn` 搜尋專案中對該 package 的使用方式
   - 判斷這個漏洞是否真的影響到專案的用法
   - 產出風險評估:
     - critical: 專案直接使用了受影響的功能
     - high: 專案間接使用了受影響的功能
     - medium: 專案使用了該 package 但不涉及漏洞路徑
     - low: 專案幾乎不使用受影響的功能
   - 將評估結果告知使用者

---

## Phase 2: 依賴分析

### Step 2.1: 取得依賴樹

```bash
python scripts/dep_tree.py <project_path> <package_name>
```

輸出 JSON 包含:
- `dependency_type`: direct | transitive | both
- `current_version`: 目前使用的版本
- `parent_packages`: 如果是 transitive，哪些 direct pkg 引用它
- `version_constraints`: 各 parent 對此 pkg 的版本約束
- `full_tree`: 完整依賴子樹

### Step 2.2: 判斷升級路徑

根據 `dependency_type` 分支處理:

#### Type A — 直接引用

1. 用 web search 查 PyPI 上目標版本的 `python_requires`
   - 搜尋 `{package_name} {target_version} pypi python_requires`
   - 或 `web_fetch https://pypi.org/pypi/{package_name}/{target_version}/json`
2. 比對專案的 python 版本
3. 若相容 → 可升級，進入 Phase 3
4. 若不相容 → 告知使用者 Python 版本不滿足

#### Type B — 間接引用 (transitive)

1. 找到所有直接引用此 pkg 的 parent packages
2. 檢查 parent 的版本約束是否允許目標版本
3. 若 parent 本身是直接引用 → 走 Type A 流程升級 parent
4. 若無法透過升級 parent 解決 → 走衝突解決流程

#### Type C — 直接 + 間接引用

最複雜的情況。你需要:
1. 先做 Type A 的 python 相容性檢查
2. 再檢查所有 parent 的版本約束
3. 如果有衝突 → 走衝突解決流程

### Step 2.3: 衝突解決 (如有衝突)

**這是你作為 LLM 的關鍵價值所在。** 不要只給出機械式的「升級 parent」建議。

你要綜合分析整個依賴圖，考慮以下策略並排序:

1. **同時升級** — 能否同時升級衝突的 parent packages？
2. **版本範圍** — 是否有中間版本同時滿足所有約束？
3. **約束寬鬆** — 衝突是否只是宣告性的？(實際 API 相容但 parent 的 requirements 寫太緊)
4. **替代套件** — 是否有 drop-in replacement 可以繞過衝突？
5. **分階段升級** — 先升到某個中間版本，再升到目標版本
6. **Override** — 使用 pip --force / poetry 的 dependency overrides

對每個方案給出:
- 具體操作步驟
- 風險評估
- 預估工作量

然後 **暫停，等使用者選擇方案** 再繼續。

---

## Phase 3: Breaking Change 分析

> **這是整個流程中你的 LLM 能力最重要的階段。**
> 你需要同時從 Changelog 和 Git Diff 兩個維度分析，然後合併結果。

### Step 3.1: Changelog 分析

```bash
python scripts/fetch_changelog.py <package_name> <git_repo_url>
```

script 會嘗試以下來源並輸出原文:
- PyPI metadata 中的 changelog URL
- GitHub Releases API
- 常見路徑: CHANGELOG.md, CHANGES.rst, HISTORY.md

**你的分析任務:**

拿到 changelog 原文後，你要:

1. 定位從 `current_version` 到 `target_version` 之間的所有條目
2. 逐條分類:
   - 🔴 BREAKING — API 刪除、更名、行為變更、預設值變更
   - 🟡 DEPRECATED — 標記為棄用但仍可用
   - 🟢 FEATURE — 新增功能
   - ⚪ FIX — Bug 修復

3. **特別注意隱含 breaking change 的措辭** (讀 `references/breaking_change_patterns.md`):
   - "improved default behavior" → 預設行為變更
   - "now returns X instead of Y" → 回傳型別變更
   - "parameter X is now required" → 簽名變更
   - "moved from A to B" → 模組路徑變更

4. 對每個 BREAKING/DEPRECATED 條目，記錄:
   - 影響的模組路徑和符號
   - 舊用法 → 新用法
   - 你的信心分數 (0.0~1.0)

### Step 3.2: Git Diff 分析

```bash
bash scripts/git_diff.sh <git_repo_url> <current_version> <target_version>
```

輸出: 兩個版本 tag 之間的 `*.py` diff

**你的分析任務:**

> 這是 AST 做不到、只有 LLM 能做的部分。

如果 diff 很大，分批閱讀 (每次一個檔案或一組相關檔案)。
聚焦在以下 public API 變更:

1. **被刪除的** public function / class / method
2. **函式簽名變更** — 參數增減、預設值改變、type hint 變更
3. **回傳值型別變更** — 例: list → generator (會影響 len/index 操作)
4. **行為邏輯變更** — 同一函式的輸出結果不同
5. **預設參數值變更** — 例: timeout 從 None 改為 30
6. **Exception 類型變更** — 例: ValueError 改為 TypeError
7. **`__all__` 清單變更** — 影響 `from pkg import *`
8. **新增 `warnings.warn` / `@deprecated`** — 標記即將棄用

判斷準則:
- `_` 開頭的是 private → 忽略
- 新增帶預設值的參數 → 通常不 breaking
- 刪除參數或改變順序 → breaking

### Step 3.3: 合併分析結果

將 Changelog 和 Git Diff 兩份分析合併:
- **去重**: 同一個變更可能兩邊都提到
- **交叉驗證**: 兩邊都提到 → 信心提高
- **補充**: Diff 發現但 changelog 沒提 → 標記為「未記錄的 breaking change ⚠️」
- **按影響程度排序**: 刪除 > 簽名變更 > 行為變更 > 棄用

產出最終的 breaking changes 清單，格式:

```
## Breaking Changes 清單

### 🔴 BC-001: `module.func_name` 已被移除
- 來源: Changelog ✅ + Git Diff ✅
- 信心: 0.98
- 舊用法: `from pkg.module import func_name`
- 新用法: `from pkg.module import new_func_name`
- 遷移說明: ...

### 🟡 BC-002: `module.old_api` 標記為棄用
- 來源: Git Diff ✅ (Changelog 未記錄 ⚠️)
- 信心: 0.75
- 說明: 新增了 DeprecationWarning，建議改用 new_api
```

---

## Phase 4: 專案程式碼影響分析

### Step 4.1: AST 掃描

```bash
python scripts/ast_scanner.py <project_path> <package_name>
```

輸出 JSON，包含每個 .py 檔案中:
- import 了 package 的哪些模組
- 使用了哪些 symbol (函式、類別、常數)
- 使用的行號
- 周圍 ±5 行的程式碼上下文

### Step 4.2: 交叉比對

將 AST 掃描結果與 Phase 3 的 breaking changes 清單交叉比對，
找出專案中實際受影響的程式碼位置。

### Step 4.3: 生成修改建議

**這是你作為 LLM 的核心價值 — 不只標記問題，還要提供解法。**

對每個受影響的程式碼位置:

1. 閱讀周圍上下文 (至少前後 10 行)
2. 理解這段程式碼的業務邏輯意圖
3. 結合 breaking change 的遷移說明
4. 生成具體的修改程式碼 (不是泛泛的建議)
5. 確保:
   - 保持原有的程式碼風格 (縮排、引號、命名)
   - 新的 import 路徑正確
   - 如有多種修改方式，選最簡潔且向後相容的
   - 不修改與 breaking change 無關的程式碼

6. 以 unified diff 格式展示每處修改

### Step 4.4: 預覽確認

將所有待修改的檔案和 diff 展示給使用者，**暫停等待確認** 再繼續。

列出:
- 總共影響 N 個檔案、M 處修改
- 每個檔案的修改摘要
- 完整的 diff 預覽

---

## Phase 5: 執行升級

### Step 5.1: 建立 Git 分支

**在修改任何專案內容之前，必須先建立新的 feature 分支。**

分支命名規則:
```bash
git checkout -b feature/Update-{PackageName}-to-{TargetVersion}
```

範例:
```bash
git checkout -b feature/Update-requests-to-2.32.0
git checkout -b feature/Update-django-to-5.1
```

如果是修復 CVE:
```bash
git checkout -b fix/CVE-{CVE-ID}-{PackageName}
# 範例: git checkout -b fix/CVE-2024-35195-cryptography
```

### Step 5.2: 環境備份

```bash
bash scripts/snapshot_env.sh <project_path> save
```

### Step 5.3: 更新依賴宣告檔

**重要**: 必須同時更新依賴宣告檔和鎖定檔案,不能只更新鎖定檔案!

根據 pkg_manager 執行對應的更新命令:

#### For pip:

**檢查是否有 lock 檔案** (從 Phase 0 的 `pip_lock_file` 欄位):

**情況 A: 使用 pip-tools (有 requirements.in)**

```bash
# 1. 手動編輯 requirements.in
# 例: requests==2.28.0 → requests==2.32.0

# 2. 重新編譯產生 requirements.txt (lock 檔案)
pip-compile requirements.in --output-file requirements.txt

# 或只升級特定套件
pip-compile --upgrade-package requests requirements.in

# 3. 安裝
pip-sync requirements.txt
```

**如果沒有 pip-compile 命令**:
```bash
pip install pip-tools
```

**情況 B: 有自定義 lock 檔案 (如 requirements.lock)**

**暫停並詢問使用者**:
```
偵測到專案使用 lock 檔案: {pip_lock_file}

請確認更新流程:
1. 更新 requirements.txt 中的版本約束
2. 重新產生 {pip_lock_file}

產生 lock 檔案的方式:
a) 使用 pip freeze: pip install -r requirements.txt && pip freeze > {pip_lock_file}
b) 使用專案自定義腳本 (如 make lock)
c) 手動管理

請選擇:
[1] 自動執行方式 a (pip freeze)
[2] 告訴我使用哪個腳本
[3] 我會手動處理,繼續下一步
```

根據使用者選擇執行對應操作。

**情況 C: 無 lock 檔案 (只有 requirements.txt)**

```bash
# 1. 手動編輯 requirements.txt
# 例: requests==2.28.0 → requests==2.32.0

# 2. 安裝新版本
pip install --upgrade <package>==<version>

# 或從檔案安裝
pip install -r requirements.txt
```

#### For poetry:

```bash
# 使用 poetry add 自動更新 pyproject.toml 和 poetry.lock
poetry add <package>@<version>

# 範例
poetry add requests@2.32.0
```

**`poetry add` 會自動**:
1. ✅ 更新 `pyproject.toml` 中的版本約束
2. ✅ 更新 `poetry.lock`
3. ✅ 安裝新版本

**不要只執行 `poetry lock` 或 `poetry update`**,這些命令不會修改 `pyproject.toml`!

#### For uv (專案模式):

```bash
# 使用 uv add 自動更新 pyproject.toml 和 uv.lock
uv add "<package>>=<version>"

# 範例
uv add "requests>=2.32.0"
# 或精確版本
uv add "requests==2.32.0"
```

**`uv add` 會自動**:
1. ✅ 更新 `pyproject.toml` 的 dependencies 列表
2. ✅ 更新 `uv.lock`
3. ✅ 安裝新版本

**不要只執行 `uv lock --upgrade-package`**,這只會更新鎖定檔案,不會更新 `pyproject.toml`!

#### For uv (傳統 pip 模式):

```bash
# 1. 手動編輯 requirements.txt
# 例: requests==2.28.0 → requests==2.32.0

# 2. 安裝新版本
uv pip install -r requirements.txt
```

**驗證更新**:

更新後,檢查以下檔案確認版本已正確更新:

- pip: `requirements.txt` 或 `pyproject.toml`
- poetry: `pyproject.toml` (檢查 `[tool.poetry.dependencies]`) 和 `poetry.lock`
- uv: `pyproject.toml` (檢查 `dependencies` 列表) 和 `uv.lock`

### Step 5.4: 套用程式碼修改

使用 file editing 工具 (str_replace) 逐一套用 Phase 4 確認的修改。

---

## Phase 6: 測試驗證

### Step 6.1: 識別相關測試

根據 affected_files 推斷對應的 test 檔案:
- `src/foo/bar.py` → `tests/test_bar.py` 或 `tests/foo/test_bar.py`
- 也檢查 `conftest.py` 中對該 package 的 fixture

### Step 6.2: 分層執行測試

```bash
# 第一輪: 只跑受影響的測試
bash scripts/run_tests.sh <project_path> --files <test_files>

# 第二輪 (若第一輪通過): 跑完整測試
bash scripts/run_tests.sh <project_path> --all
```

### Step 6.3: 測試失敗診斷

> **這是你作為 LLM 第二重要的分析任務。**

如果有測試失敗，你需要做 **三向交叉分析**:

1. 閱讀完整的 pytest traceback
2. 閱讀失敗測試的原始碼
3. 閱讀被測試的業務程式碼 (source code)
4. 參照本次升級的 breaking changes 清單

然後對每個失敗的測試判斷:

**根因分類:**
- `SOURCE_CODE` — 業務程式碼還需要修改 (Phase 4 漏掉的)
- `TEST_CODE` — 測試程式碼需要修改 (測試了已變更的行為)
- `BOTH` — 兩者都需要修改
- `CONFIG` — 配置問題 (fixture、conftest、mock 設定)

**判斷準則:**
- ImportError / ModuleNotFoundError → 通常是 SOURCE_CODE
- AssertionError 且 assert 值反映行為變更 → TEST_CODE
- TypeError (參數不匹配) → 看是業務碼還是測試碼直接呼叫
- 測試 mock 了被變更的 API → TEST_CODE
- 測試直接呼叫了被刪除的 API → TEST_CODE

### Step 6.4: 處理測試失敗

#### 如果是 SOURCE_CODE 問題:
- 生成額外的程式碼修改
- 套用修改
- 重新跑測試

#### 如果是 TEST_CODE 問題:
- **必須暫停，等使用者確認**
- 向使用者解釋:
  - 為什麼這個測試需要改 (不是 bug，而是上游行為的預期變更)
  - 具體要怎麼改
  - 改後的測試仍然在驗證什麼
- 使用者確認後才修改測試
- 修改後重新跑測試

### Step 6.5: 迴圈

重複 6.2 ~ 6.4 直到所有測試通過 (或使用者決定停止)。

最大迴圈次數: 3 次。超過 3 次仍有失敗 → 停下來，把所有資訊報告給使用者。

---

## Phase 7: 產出報告與 Commit Message

### Step 7.1: 遷移報告

> 不要用模板填空。用你自己的語言，寫一份有邏輯、有重點的報告。

報告結構 (參照 `templates/report_structure.md` 但不要死板照抄):

1. **Executive Summary** — 3-5 句話總結整個升級
   - 升了什麼、從哪個版本到哪個版本、為什麼
   - 有幾個 breaking changes、影響了幾個檔案
   - 測試結果

2. **依賴分析** — 引用類型、衝突處理

3. **Breaking Changes 詳情** — 每個變更的影響和解決方式

4. **程式碼修改清單** — 每個檔案改了什麼、為什麼

5. **測試結果** — 通過/失敗、是否修改了測試程式

6. **後續建議** — 還有哪些相關套件可能需要更新

7. **回退指南** — 如果需要回退，怎麼做

### Step 7.2: Git Commit Message

寫一個符合 Conventional Commits 規範的 commit message (英文):

- 第一行: `type(scope): description` (≤72 字元)
- Body: 解釋「為什麼」(不只是「做了什麼」)
- 如果是 CVE: 包含 CVE 編號和嚴重性
- 如果有 BREAKING CHANGE: 使用 footer

### Step 7.3: 建立 Pull Request

將所有變更 commit 後,建立 Pull Request:

```bash
# Commit 所有變更
git add .
git commit -m "<Phase 7.2 產生的 commit message>"

# Push 到遠端
git push -u origin feature/Update-{PackageName}-to-{TargetVersion}

# 建立 PR (如有 gh CLI)
gh pr create --title "chore: upgrade {package} to {version}" \
  --body "$(cat <migration_report.md>)"
```

PR 內容應包含:
- Phase 7.1 產生的完整遷移報告作為 PR description
- 標記為 `dependencies` / `security` label (如果是 CVE 修復)
- 指定 reviewers (如有需要)

### Step 7.4: 完成

將報告輸出給使用者，並提供:
1. 報告全文
2. 已建立的 commit 和 branch 資訊
3. Pull Request URL (如已建立)
4. 回退命令 (以防需要)

---

## 錯誤處理

- **Changelog 抓不到**: 只依賴 git diff 分析，告知使用者
- **Git repo 找不到**: 只依賴 changelog，告知使用者
- **兩者都失敗**: 用 web search 搜尋 breaking changes 資訊
- **測試持續失敗**: 3 次迴圈後停止，報告給使用者
- **環境損壞**: 用 snapshot_env.sh restore 回退

```bash
# 回退命令
bash scripts/snapshot_env.sh <project_path> restore
```

---

## 使用者確認點一覽

在以下時間點，你必須暫停等待使用者確認，不可自動繼續:

| 時間點 | 你要提供的資訊 |
|--------|-------------|
| Phase 2.3: 衝突解決方案 | 多種方案 + 風險評估 + 推薦 |
| Phase 4.4: 程式碼修改預覽 | 完整 diff + 每處修改的理由 |
| Phase 5.1: 建立 Git 分支 | 分支名稱、即將開始修改 |
| Phase 6.4: 測試程式修改 | 為什麼要改 + 改後仍驗證什麼 |
| Phase 7.3: 建立 Pull Request | PR 資訊、是否建立 PR |
