"""GitHub Pages status scanner.

This scanner is used by both the Markdown report and the HTML dashboard.

Primary signal (canonical):
  GET /repos/{owner}/{repo}/pages

We call it via the authenticated `gh` CLI to avoid extra dependencies.

Important:
- In GitHub Actions, the default GITHUB_TOKEN may not be able to read other
  repos' Pages settings even if repos are public, which can cause false 404s.
  To reduce false positives, we fall back to checking the public Pages URL.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from typing import Optional

try:
    from .repo_utils import get_all_repos
except ImportError:
    # Allow running as a script: `python3 src/scanner/pages_check.py`
    if __package__ is None or __package__ == "":
        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        if repo_root not in sys.path:
            sys.path.insert(0, repo_root)
        from src.scanner.repo_utils import get_all_repos
    else:
        raise


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


def _pages_public_url(repo_full_name: str) -> str:
    # repo_full_name = "ai-village-agents/repo-name"
    repo_name = repo_full_name.split("/", 1)[1]
    return f"https://ai-village-agents.github.io/{repo_name}/"


def _curl_status_code(url: str) -> Optional[int]:
    """Return HTTP status code from a GET, or None on execution error."""
    cmd = [
        "curl",
        "-s",
        "-o",
        "/dev/null",
        "-w",
        "%{http_code}",
        "--max-time",
        "10",
        url,
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        return None
    try:
        return int((proc.stdout or "").strip())
    except ValueError:
        return None


def check_pages_status(repo: str) -> str:
    """Checks the GitHub Pages status for a repository.

    Returns a short status string that downstream reports render directly.

    Status meanings:
    - ✅ Live (...): Pages is enabled (or public site is live).
    - 🚫 Admin Blocked: Pages endpoint not found AND public site not live.
      (This typically means Pages isn't enabled and requires repo admin.)
    - ⚠️ Error: anything else (403, network errors, unexpected output).
    """

    # Primary: canonical GitHub API Pages endpoint.
    cmd = ["gh", "api", f"repos/{repo}/pages"]
    proc = subprocess.run(cmd, capture_output=True, text=True)

    if proc.returncode == 0:
        try:
            data = json.loads(proc.stdout) if proc.stdout else {}
        except json.JSONDecodeError:
            data = {}
        html_url = data.get("html_url") or ""
        return f"✅ Live ({html_url})" if html_url else "✅ Live"

    http_status = _extract_http_status(proc.stderr)

    # If the API call fails (403/404/other), fall back to the public Pages URL
    # to reduce false positives when the token lacks permissions.
    if http_status != 200:
        public_url = _pages_public_url(repo)
        public_status = _curl_status_code(public_url)
        if public_status == 200:
            return f"✅ Live ({public_url})"
        if public_status == 404:
            return "🚫 Admin Blocked"
        # public_status is something else (e.g., 500, 503, etc.)
        api_status = http_status if http_status is not None else "unknown"
        return f"⚠️ Error: API HTTP {api_status}, public check {public_status}"

    err = (proc.stderr or "").strip()
    if err:
        # Trim to keep table readable.
        err = err.splitlines()[0][:200]
        return f"⚠️ Error: {err}"

    return "⚠️ Error: Unknown failure"


def scan_pages_status():
    repos = get_all_repos()
    print(f"Scanning Pages status for {len(repos)} repositories...\n")

    report = {}
    for repo in repos:
        status = check_pages_status(repo)
        report[repo] = status
        print(f"{repo:<45} | {status}")

    return report


if __name__ == "__main__":
    scan_pages_status()
