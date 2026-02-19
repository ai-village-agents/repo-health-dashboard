"""GitHub Pages status scanner.

Uses the GitHub REST API endpoint:
  GET /repos/{owner}/{repo}/pages

We call it via the authenticated `gh` CLI to avoid extra dependencies.

Notes:
- HTTP 200 => Pages enabled.
- HTTP 404 => Pages not enabled.
- HTTP 403 => Forbidden (token/permissions/org policy).
"""

from __future__ import annotations

import json
import re
import subprocess
from typing import Dict, Optional

from .repo_utils import get_all_repos


_HTTP_RE = re.compile(r"HTTP\s+(\d{3})")


def _extract_http_status(stderr: str) -> Optional[int]:
    if not stderr:
        return None
    m = _HTTP_RE.search(stderr)
    if not m:
        return None
    try:
        return int(m.group(1))
    except ValueError:
        return None


def scan_pages_status() -> Dict[str, dict]:
    """Return repo_full_name -> status dict.

    Status dict fields:
      enabled: bool
      status: str  (enabled|not_enabled|forbidden|error)
      http_status: int|None
      pages_url: str|None
    """
    results: Dict[str, dict] = {}
    repos = get_all_repos()

    for repo in repos:
        cmd = ["gh", "api", f"repos/{repo}/pages"]
        proc = subprocess.run(cmd, capture_output=True, text=True)

        if proc.returncode == 0:
            pages_url = None
            try:
                data = json.loads(proc.stdout) if proc.stdout else {}
                pages_url = data.get("html_url") or data.get("url")
            except json.JSONDecodeError:
                pages_url = None

            results[repo] = {
                "enabled": True,
                "status": "enabled",
                "http_status": 200,
                "pages_url": pages_url,
            }
            continue

        http_status = _extract_http_status(proc.stderr)
        if http_status == 404:
            status = "not_enabled"
        elif http_status == 403:
            status = "forbidden"
        else:
            status = "error"

        results[repo] = {
            "enabled": False,
            "status": status,
            "http_status": http_status,
            "pages_url": None,
        }

    return results


if __name__ == "__main__":
    out = scan_pages_status()
    enabled = sum(1 for v in out.values() if v.get("enabled"))
    print(f"Scanned {len(out)} repos. Enabled: {enabled}.")
    for repo, info in out.items():
        if not info.get("enabled"):
            print(f"- {repo}: {info.get('status')} ({info.get('http_status')})")
