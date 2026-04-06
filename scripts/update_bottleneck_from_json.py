#!/usr/bin/env python3
"""Update docs/github_pages_admin_bottleneck.md from JSON (and optional scan).

- Reads blocked repositories from data/pages_blocked_state.json.
- Optionally runs scan_pages_status() to refresh live/other counts and live list.
- Rewrites the bottleneck markdown with updated counts and repository lists.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

NB_HYPHEN = "\u2011"
REPO_ROOT = Path(__file__).resolve().parent.parent
DOC_PATH = REPO_ROOT / "docs" / "github_pages_admin_bottleneck.md"
STATE_PATH = REPO_ROOT / "data" / "pages_blocked_state.json"


def _ensure_repo_on_path() -> None:
    repo_root = str(REPO_ROOT)
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)


def load_blocked_state() -> Tuple[List[str], Optional[int], Optional[str]]:
    """Return (blocked_list, total_repos, error_message)."""
    if not STATE_PATH.exists():
        return [], None, f"State file not found: {STATE_PATH}"

    try:
        data = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [], None, f"Invalid JSON in {STATE_PATH}: {exc}"

    blocked = data.get("blocked_repositories") or []
    total_repos = data.get("total_repositories_scanned")
    return blocked, total_repos, None


def maybe_scan_pages_status(run_scan: bool) -> Tuple[Optional[Dict[str, str]], Optional[str]]:
    """Run scan_pages_status() when requested; return (status_map, error)."""
    if not run_scan:
        return None, "Scan skipped (flagged via --no-scan)."

    _ensure_repo_on_path()
    try:
        from src.scanner.pages_check import scan_pages_status  # type: ignore
    except Exception as exc:  # pragma: no cover - defensive import
        return None, f"Unable to import scan_pages_status: {exc}"

    try:
        status_map: Dict[str, str] = scan_pages_status()
        return status_map, None
    except Exception as exc:  # pragma: no cover - network/gh failures
        return None, f"Error running scan_pages_status: {exc}"


def to_nb_hyphen(text: str) -> str:
    return text.replace("-", NB_HYPHEN)


def format_repo_list(repos: Iterable[str]) -> List[str]:
    return [f"- `{to_nb_hyphen(repo)}`" for repo in repos]


def extract_live_list(status_map: Optional[Dict[str, str]], blocked: List[str]) -> List[str]:
    if not status_map:
        return []
    blocked_set = set(blocked)
    live = [
        repo for repo, status in status_map.items() if status.startswith("✅") and repo not in blocked_set
    ]
    live.sort(key=lambda r: r.lower())
    return live


def compute_counts(
    status_map: Optional[Dict[str, str]],
    blocked: List[str],
    total_from_json: Optional[int],
) -> Tuple[int, int, int]:
    blocked_count = len(blocked)
    if status_map is not None:
        total = len(status_map)
        live = sum(1 for s in status_map.values() if str(s).startswith("✅"))
        other = max(total - live - blocked_count, 0)
        return total, live, other

    total = total_from_json or blocked_count
    live = max(total - blocked_count, 0)
    other = max(total - live - blocked_count, 0)
    return total, live, other


def render_overview(blocked_count: int, total_repos: int) -> str:
    lines = [
        "## Overview",
        "",
        "GitHub Pages deployment for repositories under the `ai\u2011village\u2011agents` organization "
        "faces a **manual admin\u2011enablement bottleneck**. When a repository's GitHub Pages site is "
        "first deployed via GitHub Actions, the GitHub Pages feature must be enabled by a repository "
        "administrator via the **Settings → Pages** tab. The GitHub Actions token (`GITHUB_TOKEN`) lacks "
        "the necessary privileges to perform this initial enablement.",
        "",
        "This results in a **404 status** for the site (`https://ai\u2011village\u2011agents.github.io/<repo-name>/`) "
        "even when the build workflow completes successfully. The Pages site remains inaccessible until an "
        "admin manually visits the repository settings and enables GitHub Pages.",
        "",
        f"**Status:** The bottleneck persists for {blocked_count} repositories. Since the previous report "
        f"(Day 323, February 18), the organization has grown from 32 to {total_repos} repositories, and "
        "the three previously blocked repositories (`gpt5\u2011breaking\u2011news`, "
        "`village\u2011operations\u2011handbook`, `lessons\u2011from\u2011293\u2011days`) are now live.",
        "",
    ]
    return "\n".join(lines)


def render_blocked_section(blocked: List[str]) -> str:
    lines = [
        f"## Blocked Repositories ({len(blocked)})",
        "",
        "The following repositories are currently **admin\u2011blocked** "
        "(GitHub Pages not enabled, returning HTTP 404):",
        "",
    ]
    lines.extend(format_repo_list(blocked))
    lines.append("")  # trailing newline
    return "\n".join(lines)


def render_live_section(live: List[str], fallback_section: str, live_count: int) -> str:
    if live:
        lines = [
            f"## Live Repositories ({live_count})",
            "",
            "The following repositories have live GitHub Pages sites (HTTP 200):",
            "",
        ]
        lines.extend(format_repo_list(live))
        lines.append("")
        return "\n".join(lines)
    return fallback_section.strip()


def extract_existing_section(content: str, start: str, end: str) -> str:
    start_idx = content.find(start)
    end_idx = content.find(end)
    if start_idx == -1 or end_idx == -1 or end_idx <= start_idx:
        return ""
    return content[start_idx:end_idx].strip()


def render_analysis(total_repos: int, live_count: int, blocked_count: int) -> str:
    pct = (live_count / total_repos * 100) if total_repos else 0
    lines = [
        "## Analysis",
        "",
        f"1. **Growth:** The organization has expanded significantly from 32 repositories (February) "
        f"to {total_repos} repositories (April).",
        f"2. **Success rate:** {live_count}/{total_repos} repositories ({pct:.1f}%) have live Pages sites.",
        "3. **Archived repositories:** Some blocked repositories may be archived, which could explain their 404 status.",
        f"4. **Admin intervention needed:** The {blocked_count} blocked repositories require manual admin enablement "
        "of GitHub Pages via **Settings → Pages**.",
        "",
    ]
    return "\n".join(lines)


def render_next_steps() -> str:
    return "\n".join(
        [
            "## Next Steps",
            "",
            "1. **Admin review:** Check each blocked repository to determine if GitHub Pages should be enabled.",
            "2. **Archived repositories:** For archived repositories, decide whether to enable Pages or accept the 404 status.",
            "3. **Automation improvement:** Explore whether GitHub Actions permissions can be elevated or if a different "
            "deployment method could bypass this bottleneck.",
            "4. **Regular monitoring:** Update this report monthly to track progress.",
            "",
        ]
    )


def render_methodology() -> str:
    return "\n".join(
        [
            "## Methodology",
            "",
            "- Repository list fetched via GitHub CLI: `gh repo list ai-village-agents --limit 200 --json name,isArchived`",
            "- Pages status checked via HTTP request to `https://ai\u2011village\u2011agents.github.io/<repo-name>/`",
            "- Live = HTTP 200 response",
            "- Blocked = HTTP 404 response",
            "- Other = any other response (403, 500, timeout, etc.)",
            "",
        ]
    )


def render_document(
    content: str,
    total_repos: int,
    live_count: int,
    blocked: List[str],
    other_count: int,
    live_list: List[str],
) -> str:
    today_str = datetime.utcnow().strftime("%Y-%m-%d").replace("-", NB_HYPHEN)

    header_lines = [
        f"# GitHub Pages Admin{NB_HYPHEN}Enablement Bottleneck",
        "",
        f"**Date:** {today_str} (Day 370)  ",
        f"**Scanned repositories:** {total_repos}  ",
        f"**Live GitHub Pages sites:** {live_count}  ",
        f"**Admin{NB_HYPHEN}blocked repositories:** {len(blocked)}  ",
        f"**Other status:** {other_count}",
        "",
    ]

    overview = render_overview(len(blocked), total_repos)
    blocked_section = render_blocked_section(blocked)

    existing_live_section = extract_existing_section(
        content, "## Live Repositories", "## Analysis"
    )
    live_section = render_live_section(live_list, existing_live_section, live_count)

    analysis = render_analysis(total_repos, live_count, len(blocked))
    next_steps = render_next_steps()
    methodology = render_methodology()

    parts = [
        "\n".join(header_lines),
        overview,
        blocked_section,
        live_section,
        analysis,
        next_steps,
        methodology,
    ]
    return "\n".join(parts).strip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Update Pages bottleneck report.")
    parser.add_argument(
        "--no-scan",
        action="store_true",
        help="Skip running scan_pages_status(); rely solely on JSON.",
    )
    args = parser.parse_args()

    blocked, total_from_json, state_error = load_blocked_state()
    if state_error:
        print(f"[WARN] {state_error}")

    status_map, scan_error = maybe_scan_pages_status(run_scan=not args.no_scan)
    if scan_error:
        print(f"[INFO] {scan_error}")

    total_repos, live_count, other_count = compute_counts(status_map, blocked, total_from_json)
    live_list = extract_live_list(status_map, blocked)

    try:
        existing_content = DOC_PATH.read_text(encoding="utf-8")
    except FileNotFoundError:
        existing_content = ""

    new_content = render_document(
        existing_content,
        total_repos=total_repos,
        live_count=live_count,
        blocked=blocked,
        other_count=other_count,
        live_list=live_list,
    )

    DOC_PATH.write_text(new_content, encoding="utf-8")
    print(f"Updated {DOC_PATH} with {len(blocked)} blocked repositories.")
    if status_map is not None:
        print(f"Live repositories: {live_count}/{total_repos} (other: {other_count})")
    else:
        print("Live repository count derived from JSON only.")


if __name__ == "__main__":
    main()
