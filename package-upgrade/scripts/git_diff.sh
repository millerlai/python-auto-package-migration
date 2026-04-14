#!/usr/bin/env bash
# git_diff.sh - Clone repo and diff Python files between version tags
# Usage: bash git_diff.sh <repo_url> <old_version> <new_version>
# Output: Git diff of .py files between versions

set -euo pipefail

REPO_URL="$1"
OLD_VER="$2"
NEW_VER="$3"
WORK_DIR=$(mktemp -d)

# Cleanup on exit
trap 'rm -rf "$WORK_DIR"' EXIT

cd "$WORK_DIR" || exit 1

echo "Cloning repository (shallow)..." >&2
# Shallow clone with only tags
if ! git clone --bare --filter=tree:0 "$REPO_URL" repo.git 2>/dev/null; then
    echo "ERROR: Failed to clone repository: $REPO_URL" >&2
    exit 1
fi

cd repo.git || exit 1

# Function to find tag in various formats
find_tag() {
    local ver="$1"
    local patterns=("v$ver" "$ver" "release-$ver" "release/$ver" "releases/$ver")

    for pattern in "${patterns[@]}"; do
        if git rev-parse "$pattern" >/dev/null 2>&1; then
            echo "$pattern"
            return 0
        fi
    done
    return 1
}

echo "Finding tags..." >&2
OLD_TAG=$(find_tag "$OLD_VER")
NEW_TAG=$(find_tag "$NEW_VER")

if [ -z "$OLD_TAG" ]; then
    echo "ERROR: Cannot find tag for version $OLD_VER" >&2
    echo "Available tags:" >&2
    git tag --list | head -20 >&2
    exit 1
fi

if [ -z "$NEW_TAG" ]; then
    echo "ERROR: Cannot find tag for version $NEW_VER" >&2
    echo "Available tags:" >&2
    git tag --list | head -20 >&2
    exit 1
fi

echo "Comparing $OLD_TAG -> $NEW_TAG" >&2
echo "Generating diff of Python files..." >&2

# Generate diff (only .py files)
git diff "$OLD_TAG".."$NEW_TAG" -- "*.py" "**/*.py"
