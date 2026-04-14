#!/usr/bin/env python3
"""Fetch changelog for a Python package.

Usage: python fetch_changelog.py <package_name> <git_repo_url>
Output: Raw changelog text to stdout
"""

import sys
import re
import requests
from typing import Optional
from urllib.parse import urlparse


def fetch_from_pypi(package_name: str) -> Optional[str]:
    """Try to fetch changelog from PyPI metadata."""
    try:
        url = f"https://pypi.org/pypi/{package_name}/json"
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        data = response.json()
        project_urls = data.get("info", {}).get("project_urls", {})

        # Look for common changelog URL keys
        changelog_keys = ["Changelog", "Change Log", "CHANGELOG", "Release Notes", "What's New"]
        for key in changelog_keys:
            if key in project_urls:
                changelog_url = project_urls[key]
                changelog_response = requests.get(changelog_url, timeout=10)
                if changelog_response.status_code == 200:
                    return f"# Changelog from PyPI ({key})\n\n{changelog_response.text}"

        return None
    except (requests.RequestException, KeyError, ValueError):
        return None


def fetch_from_github_releases(repo_url: str) -> Optional[str]:
    """Try to fetch changelog from GitHub Releases API."""
    try:
        # Parse GitHub repo URL
        # Supports: https://github.com/owner/repo or git@github.com:owner/repo.git
        match = re.search(r'github\.com[:/]([^/]+)/([^/\.]+)', repo_url)
        if not match:
            return None

        owner, repo = match.groups()
        api_url = f"https://api.github.com/repos/{owner}/{repo}/releases"

        response = requests.get(api_url, timeout=10)
        response.raise_for_status()

        releases = response.json()
        if not releases:
            return None

        # Format releases into changelog
        changelog_parts = ["# Changelog from GitHub Releases\n"]
        for release in releases[:50]:  # Limit to recent 50 releases
            tag = release.get("tag_name", "Unknown")
            name = release.get("name", tag)
            body = release.get("body", "No release notes")
            published = release.get("published_at", "")

            changelog_parts.append(f"\n## {name} ({tag})")
            if published:
                changelog_parts.append(f"Published: {published}")
            changelog_parts.append(f"\n{body}\n")
            changelog_parts.append("---")

        return "\n".join(changelog_parts)

    except (requests.RequestException, KeyError, ValueError, IndexError):
        return None


def fetch_from_common_files(repo_url: str) -> Optional[str]:
    """Try to fetch changelog from common file locations in repo."""
    try:
        # Parse GitHub repo URL
        match = re.search(r'github\.com[:/]([^/]+)/([^/\.]+)', repo_url)
        if not match:
            return None

        owner, repo = match.groups()

        # Common changelog filenames
        changelog_files = [
            "CHANGELOG.md",
            "CHANGELOG.rst",
            "CHANGELOG.txt",
            "CHANGELOG",
            "CHANGES.md",
            "CHANGES.rst",
            "CHANGES.txt",
            "CHANGES",
            "HISTORY.md",
            "HISTORY.rst",
            "NEWS.md",
            "RELEASES.md",
        ]

        for filename in changelog_files:
            # Try main/master branch
            for branch in ["main", "master"]:
                raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{filename}"
                try:
                    response = requests.get(raw_url, timeout=10)
                    if response.status_code == 200:
                        return f"# Changelog from {filename}\n\n{response.text}"
                except requests.RequestException:
                    continue

        return None

    except (requests.RequestException, AttributeError):
        return None


def main():
    if len(sys.argv) < 3:
        print("Usage: python fetch_changelog.py <package_name> <git_repo_url>", file=sys.stderr)
        sys.exit(1)

    package_name = sys.argv[1]
    git_repo_url = sys.argv[2]

    # Try different sources in order
    changelog = None

    # 1. Try PyPI metadata
    print("# Attempting to fetch changelog...\n", file=sys.stderr)
    print("Trying PyPI metadata...", file=sys.stderr)
    changelog = fetch_from_pypi(package_name)

    # 2. Try GitHub Releases
    if not changelog:
        print("Trying GitHub Releases API...", file=sys.stderr)
        changelog = fetch_from_github_releases(git_repo_url)

    # 3. Try common changelog files
    if not changelog:
        print("Trying common changelog files...", file=sys.stderr)
        changelog = fetch_from_common_files(git_repo_url)

    # Output result
    if changelog:
        print("\nChangelog found!\n", file=sys.stderr)
        print(changelog)
    else:
        print("\nNo changelog found from any source.", file=sys.stderr)
        print("You may need to manually search for breaking changes.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
