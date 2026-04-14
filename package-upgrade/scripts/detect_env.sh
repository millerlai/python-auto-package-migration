#!/usr/bin/env bash
# detect_env.sh - Detect package manager and Python environment
# Usage: bash detect_env.sh <project_path>
# Output: JSON with environment information

set -euo pipefail

PROJECT_PATH="${1:-.}"
cd "$PROJECT_PATH" || exit 1

# Get Python version
PYTHON_VERSION=$(python3 --version 2>/dev/null | grep -oP '\d+\.\d+\.\d+' || echo "unknown")

PKG_MANAGER="unknown"
LOCKFILE=""
PIP_LOCK_FILE=""
HAS_PIP_TOOLS="false"
DEP_FILES="[]"

# Detect package manager (priority: uv > poetry > pip)
if [ -f "uv.lock" ] || grep -q '\[tool\.uv\]' pyproject.toml 2>/dev/null; then
    PKG_MANAGER="uv"
    LOCKFILE="uv.lock"
elif [ -f "poetry.lock" ] || grep -q '\[tool\.poetry\]' pyproject.toml 2>/dev/null; then
    PKG_MANAGER="poetry"
    LOCKFILE="poetry.lock"
elif [ -f "requirements.txt" ] || [ -f "setup.py" ] || [ -f "setup.cfg" ] || [ -f "pyproject.toml" ]; then
    PKG_MANAGER="pip"

    # Detect pip lock file patterns
    # Priority: requirements.in (pip-tools) > requirements.lock > requirements.txt.lock
    if [ -f "requirements.in" ]; then
        HAS_PIP_TOOLS="true"
        LOCKFILE="requirements.txt"  # pip-tools uses .txt as lock
        PIP_LOCK_FILE="requirements.txt"
    elif [ -f "requirements.lock" ]; then
        LOCKFILE="requirements.txt"
        PIP_LOCK_FILE="requirements.lock"
    elif [ -f "requirements.txt.lock" ]; then
        LOCKFILE="requirements.txt"
        PIP_LOCK_FILE="requirements.txt.lock"
    elif [ -f "requirements-lock.txt" ]; then
        LOCKFILE="requirements.txt"
        PIP_LOCK_FILE="requirements-lock.txt"
    elif [ -f "requirements/production.lock" ]; then
        LOCKFILE="requirements.txt"
        PIP_LOCK_FILE="requirements/production.lock"
    elif [ -f "requirements.txt" ]; then
        LOCKFILE="requirements.txt"
        PIP_LOCK_FILE=""  # No separate lock file
    fi
fi

# Find dependency declaration files (exclude .venv, venv, node_modules)
DEP_FILES=$(find . -maxdepth 2 \( \
    -name "requirements*.txt" -o \
    -name "pyproject.toml" -o \
    -name "setup.py" -o \
    -name "setup.cfg" \
\) -not -path "./.venv/*" \
   -not -path "./venv/*" \
   -not -path "./node_modules/*" \
   -not -path "./.git/*" 2>/dev/null | \
   jq -R -s 'split("\n") | map(select(. != ""))')

# Output JSON
cat <<EOF
{
  "pkg_manager": "$PKG_MANAGER",
  "python_version": "$PYTHON_VERSION",
  "lockfile_path": "$LOCKFILE",
  "pip_lock_file": "$PIP_LOCK_FILE",
  "has_pip_tools": $HAS_PIP_TOOLS,
  "dependency_files": $DEP_FILES
}
EOF
