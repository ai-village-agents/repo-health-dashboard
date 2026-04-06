#!/usr/bin/env python3
"""Compare two pages_blocked_state.json files and summarize changes."""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional, Set, Tuple


def load_blocked_repos(path: Path) -> Tuple[Set[str], Optional[str]]:
    """Return blocked repos set and timestamp from a pages_blocked_state.json file."""
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)

    blocked = data.get("blocked_repositories", [])
    if not isinstance(blocked, list):
        raise ValueError(f"'blocked_repositories' must be a list in {path}")

    timestamp = data.get("timestamp")
    return set(blocked), timestamp


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compare two pages_blocked_state.json files."
    )
    parser.add_argument(
        "current",
        nargs="?",
        default="data/pages_blocked_state.json",
        help="Path to current pages_blocked_state.json (default: data/pages_blocked_state.json)",
    )
    parser.add_argument(
        "previous",
        nargs="?",
        default="data/pages_blocked_state_previous.json",
        help="Path to previous pages_blocked_state.json (default: data/pages_blocked_state_previous.json)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    current_path = Path(args.current)
    previous_path = Path(args.previous)

    if not current_path.exists():
        print(f"Current file not found: {current_path}", file=sys.stderr)
        sys.exit(1)

    try:
        current_set, current_ts = load_blocked_repos(current_path)
    except (OSError, ValueError) as exc:
        print(f"Failed to read {current_path}: {exc}", file=sys.stderr)
        sys.exit(1)

    if not previous_path.exists():
        print(f"Previous file not found: {previous_path}")
        print(f"Current blocked repositories: {len(current_set)}")
        result = {
            "current_file": str(current_path),
            "previous_file": str(previous_path),
            "current_count": len(current_set),
            "previous_count": None,
            "added": [],
            "removed": [],
            "unchanged_count": len(current_set),
            "previous_exists": False,
            "current_timestamp": current_ts,
            "previous_timestamp": None,
        }
        print(json.dumps(result, indent=2))
        return

    try:
        previous_set, previous_ts = load_blocked_repos(previous_path)
    except (OSError, ValueError) as exc:
        print(f"Failed to read {previous_path}: {exc}", file=sys.stderr)
        sys.exit(1)

    added = sorted(current_set - previous_set)
    removed = sorted(previous_set - current_set)
    unchanged_count = len(current_set & previous_set)

    print(f"Current file: {current_path} (blocked: {len(current_set)})")
    if current_ts:
        print(f"  timestamp: {current_ts}")
    print(f"Previous file: {previous_path} (blocked: {len(previous_set)})")
    if previous_ts:
        print(f"  timestamp: {previous_ts}")
    print(f"Added (newly blocked): {len(added)}")
    for repo in added:
        print(f"  + {repo}")
    print(f"Removed (no longer blocked): {len(removed)}")
    for repo in removed:
        print(f"  - {repo}")
    print(f"Unchanged count: {unchanged_count}")

    result = {
        "current_file": str(current_path),
        "previous_file": str(previous_path),
        "current_count": len(current_set),
        "previous_count": len(previous_set),
        "added": added,
        "removed": removed,
        "unchanged_count": unchanged_count,
        "previous_exists": True,
        "current_timestamp": current_ts,
        "previous_timestamp": previous_ts,
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
