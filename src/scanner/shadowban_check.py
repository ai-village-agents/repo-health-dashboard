"""Shadowban / profile visibility check.

This module intentionally avoids third-party dependencies so it can run in
minimal environments (e.g., GitHub Actions) without requiring `pip install`.

We probe the public GitHub profile URLs as an *unauthenticated* request and
record the resulting HTTP status code.
"""

from __future__ import annotations

import time
import urllib.error
import urllib.request


def _fetch_status(url: str, *, timeout: float = 15.0) -> int:
    """Return HTTP status code for a GET request.

    For non-2xx responses, urllib raises HTTPError; we return its `code`.
    """
    req = urllib.request.Request(
        url,
        headers={
            # GitHub may respond differently without a UA; set a simple one.
            "User-Agent": "ai-village-repo-health-dashboard/1.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return int(getattr(resp, "status", 200))
    except urllib.error.HTTPError as e:
        return int(e.code)


def check_shadowbans() -> dict[str, dict[str, object]]:
    agents = [
        "claude-3-7-sonnet",
        "claude-opus-4-5",
        "claude-opus-4-6",
        "claude-sonnet-4-6",
        "claude-sonnet-45",
        "claudehaiku45",
        "deepseek-v32",
        "gemini-25-pro-collab",
        "gemini-3-pro-ai-village",
        "gpt-5-1",
        "gpt-5-2",
        "gpt-5-ai-village",
        "opus-4-5-claude-code",
    ]

    results: dict[str, dict[str, object]] = {}

    print("Scanning agent profiles for visibility (shadowban check)...")

    for agent in agents:
        url = f"https://github.com/{agent}"
        try:
            status = _fetch_status(url)
            results[agent] = {"status": status, "url": url}
        except Exception as e:
            results[agent] = {"status": "ERROR", "url": url, "error": str(e)}

        # Be polite.
        time.sleep(0.5)

    return results
