#!/usr/bin/env bash
# install.sh - 快速安裝 Package Upgrade Skill
# Usage: bash install.sh [--global|--project]

set -euo pipefail

# 顏色輸出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 預設安裝模式
MODE="global"

# 解析參數
if [ "${1:-}" = "--project" ]; then
    MODE="project"
fi

echo -e "${BLUE}=========================================="
echo "Package Upgrade Skill 安裝程式"
echo -e "==========================================${NC}"
echo ""

# 檢查是否在專案根目錄
if [ ! -d "package-upgrade" ]; then
    echo -e "${RED}錯誤: 請在專案根目錄執行此腳本${NC}"
    echo "目前路徑: $(pwd)"
    echo "預期看到: package-upgrade/ 目錄"
    exit 1
fi

# 安裝目標
if [ "$MODE" = "global" ]; then
    TARGET_DIR="$HOME/.claude/skills/package-upgrade"
    echo -e "${GREEN}安裝模式: 全域安裝${NC}"
    echo "安裝位置: $TARGET_DIR"
else
    TARGET_DIR="./.claude/skills/package-upgrade"
    echo -e "${GREEN}安裝模式: 專案級安裝${NC}"
    echo "安裝位置: $TARGET_DIR"
fi

echo ""
read -p "繼續安裝? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "安裝已取消"
    exit 0
fi

# 建立目標目錄
echo ""
echo -e "${BLUE}步驟 1/5: 建立目錄${NC}"
mkdir -p "$(dirname "$TARGET_DIR")"

if [ -d "$TARGET_DIR" ]; then
    echo -e "${YELLOW}警告: 目標目錄已存在,將會覆蓋${NC}"
    read -p "確定要覆蓋嗎? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "安裝已取消"
        exit 0
    fi
    rm -rf "$TARGET_DIR"
fi

# 複製檔案
echo ""
echo -e "${BLUE}步驟 2/5: 複製檔案${NC}"
cp -r package-upgrade "$TARGET_DIR"
echo -e "${GREEN}✓ 檔案已複製${NC}"

# 設定執行權限
echo ""
echo -e "${BLUE}步驟 3/5: 設定執行權限${NC}"
chmod +x "$TARGET_DIR"/scripts/*.sh
chmod +x "$TARGET_DIR"/scripts/*.py
echo -e "${GREEN}✓ 執行權限已設定${NC}"

# 檢查並安裝 Python 依賴
echo ""
echo -e "${BLUE}步驟 4/5: 檢查 Python 依賴${NC}"

MISSING_DEPS=()

if ! python3 -c "import pipdeptree" 2>/dev/null; then
    MISSING_DEPS+=("pipdeptree")
fi

if ! python3 -c "import requests" 2>/dev/null; then
    MISSING_DEPS+=("requests")
fi

if [ ${#MISSING_DEPS[@]} -gt 0 ]; then
    echo -e "${YELLOW}缺少依賴: ${MISSING_DEPS[*]}${NC}"
    read -p "是否安裝? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        pip install "${MISSING_DEPS[@]}"
        echo -e "${GREEN}✓ 依賴已安裝${NC}"
    else
        echo -e "${YELLOW}⚠ 跳過依賴安裝,稍後請手動執行:${NC}"
        echo "  pip install ${MISSING_DEPS[*]}"
    fi
else
    echo -e "${GREEN}✓ 所有依賴已安裝${NC}"
fi

# 檢查系統工具
echo ""
echo -e "${BLUE}步驟 5/5: 檢查系統工具${NC}"

MISSING_TOOLS=()

if ! command -v jq &> /dev/null; then
    MISSING_TOOLS+=("jq")
fi

if ! command -v git &> /dev/null; then
    MISSING_TOOLS+=("git")
fi

if [ ${#MISSING_TOOLS[@]} -gt 0 ]; then
    echo -e "${YELLOW}⚠ 缺少系統工具: ${MISSING_TOOLS[*]}${NC}"
    echo ""
    echo "安裝建議:"
    for tool in "${MISSING_TOOLS[@]}"; do
        case $tool in
            jq)
                echo "  jq:"
                echo "    macOS: brew install jq"
                echo "    Ubuntu/Debian: sudo apt-get install jq"
                ;;
            git)
                echo "  git:"
                echo "    macOS: xcode-select --install"
                echo "    Ubuntu/Debian: sudo apt-get install git"
                ;;
        esac
    done
else
    echo -e "${GREEN}✓ 所有系統工具已安裝${NC}"
fi

# 安裝完成
echo ""
echo -e "${GREEN}=========================================="
echo "✓ 安裝完成!"
echo -e "==========================================${NC}"
echo ""
echo "安裝位置: $TARGET_DIR"
echo ""
echo -e "${BLUE}下一步:${NC}"
echo ""
echo "1. 驗證安裝:"
echo "   bash verify_installation.sh"
echo ""
echo "2. 測試使用:"
echo "   claude"
echo "   # 然後輸入:"
echo "   list available skills"
echo ""
echo "3. 開始使用:"
echo "   升級 requests 到 2.32.0"
echo "   修復 CVE-2024-35195"
echo ""

if [ ${#MISSING_DEPS[@]} -gt 0 ] || [ ${#MISSING_TOOLS[@]} -gt 0 ]; then
    echo -e "${YELLOW}⚠ 注意: 請先安裝缺少的依賴和工具${NC}"
fi

echo ""
echo "更多資訊請參考:"
echo "  - INSTALLATION_GUIDE.md"
echo "  - package-upgrade/README.md"
