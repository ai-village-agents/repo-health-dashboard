"""Generate an admin notification for GitHub Pages enablement.

This script scans all organization repositories, identifies those whose
GitHub Pages are admin-blocked (e.g., 404 or "Admin Blocked"), and emits:
- docs/admin_notification.md: concise Markdown for admins
- data/pages_blocked_state.json: state snapshot for future diffs

Run from repo root:
    python3 scripts/generate_admin_notification.py
"""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime
from typing import Dict, List, Tuple


def _import_scanner_modules():
    """Import scanner modules, allowing execution from repo root or elsewhere."""
    try:
        from src.scanner.pages_check import scan_pages_status  # type: ignore
        from src.scanner.repo_utils import ORG  # type: ignore
        return scan_pages_status, ORG
    except ImportError:
        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        if repo_root not in sys.path:
            sys.path.insert(0, repo_root)
        from src.scanner.pages_check import scan_pages_status  # type: ignore
        from src.scanner.repo_utils import ORG  # type: ignore
        return scan_pages_status, ORG


def is_admin_blocked(status: str) -> bool:
    """Return True if the status indicates an admin block or 404."""
    s = status.lower()
    return ("admin" in s and "block" in s) or "404" in s


def extract_pages_url(status: str, org: str, repo_name: str) -> str:
    """Pull a URL out of the status, or fall back to the standard Pages URL."""
    m = re.search(r"\((https?://[^)]+)\)", status)
    if m:
        return m.group(1).strip()
    return f"https://{org}.github.io/{repo_name}/"


def ensure_directories():
    os.makedirs("scripts", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    os.makedirs("docs", exist_ok=True)


def build_markdown_report(
    date_str: str,
    total_repos: int,
    live_count: int,
    blocked_rows: List[Tuple[str, str, str, str]],
) -> str:
    """Return the Markdown report contents."""
    lines = [
        f"# GitHub Pages Admin Enablement Request - {date_str}",
        "",
        "Summary:",
        f"- Total repositories scanned: {total_repos}",
        f"- Live GitHub Pages: {live_count}",
        f"- Admin-blocked Pages: {len(blocked_rows)}",
        "",
        "Instructions:",
        "- For each repository, visit Settings -> Pages and click Enable.",
        "",
    ]

    if not blocked_rows:
        lines.append("No admin-blocked repositories detected 🎉")
        return "\n".join(lines)

    lines.append("| Repository | GitHub Pages URL | Settings Page Link |")
    lines.append("| --- | --- | --- |")
    for repo, display_name, pages_url, settings_url in blocked_rows:
        # Include a checkbox in the repository column to track completion.
        repo_cell = f"[ ] {display_name}"
        lines.append(f"| {repo_cell} | {pages_url} | {settings_url} |")

    return "\n".join(lines)


def save_json_state(timestamp: str, blocked: List[str], total_repos: int) -> None:
    payload = {
        "timestamp": timestamp,
        "blocked_repositories": blocked,
        "total_repositories_scanned": total_repos,
    }
    with open("data/pages_blocked_state.json", "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


def main():
    ensure_directories()
    scan_pages_status, ORG = _import_scanner_modules()

    print("Starting GitHub Pages admin notification generation...\n")

    try:
        status_map: Dict[str, str] = scan_pages_status()
    except Exception as exc:  # pragma: no cover - defensive guardrail
        print(f"Error while scanning Pages status: {exc}", file=sys.stderr)
        sys.exit(1)

    blocked_rows: List[Tuple[str, str, str, str]] = []
    blocked_repo_names: List[str] = []
    live_count = 0

    for repo_full_name, status in status_map.items():
        repo_name = repo_full_name.split("/", 1)[1]
        if status.startswith("✅"):
            live_count += 1
        if is_admin_blocked(status):
            pages_url = extract_pages_url(status, ORG, repo_name)
            settings_url = f"https://github.com/{ORG}/{repo_name}/settings/pages"
            blocked_rows.append((repo_full_name, repo_name, pages_url, settings_url))
            blocked_repo_names.append(repo_full_name)

    total_repos = len(status_map)
    date_str = datetime.utcnow().strftime("%Y-%m-%d")
    timestamp = datetime.utcnow().isoformat() + "Z"

    markdown = build_markdown_report(
        date_str=date_str,
        total_repos=total_repos,
        live_count=live_count,
        blocked_rows=blocked_rows,
    )

    md_path = "docs/admin_notification.md"
    try:
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(markdown)
        print(f"\nMarkdown report written to {md_path}")
    except Exception as exc:
        print(f"Failed to write markdown report: {exc}", file=sys.stderr)

    try:
        save_json_state(timestamp, blocked_repo_names, total_repos)
        print("JSON state written to data/pages_blocked_state.json")
    except Exception as exc:
        print(f"Failed to write JSON state: {exc}", file=sys.stderr)

    print("\nDone.")


if __name__ == "__main__":
    main()
