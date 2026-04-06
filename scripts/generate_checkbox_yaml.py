#!/usr/bin/env python3
"""
Generate YAML checkbox options for blocked repositories.

Usage:
  python scripts/generate_checkbox_yaml.py > blocked_checkboxes.yaml
  python scripts/generate_checkbox_yaml.py path/to/pages_blocked_state.json
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Iterable, TextIO

DEFAULT_INPUT = Path("data/pages_blocked_state.json")


def load_repositories(path: Path) -> list[str]:
    """Return the blocked repository names from the JSON file."""
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)

    repos = data.get("blocked_repositories")
    if not isinstance(repos, list):
        raise ValueError("blocked_repositories is missing or not a list")

    return [str(repo) for repo in repos]


def emit_yaml(repositories: Iterable[str], output: TextIO) -> None:
    """Write the YAML list of checkbox options to the given stream."""
    for repo in repositories:
        output.write(f"- label: {json.dumps(repo)}\n")
        output.write("  required: false\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Read a pages_blocked_state.json file and emit a YAML list of "
            "checkbox options that can be pasted into a GitHub issue template."
        )
    )
    parser.add_argument(
        "input_json",
        nargs="?",
        type=Path,
        default=DEFAULT_INPUT,
        help=f"Path to pages_blocked_state.json (default: {DEFAULT_INPUT})",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    repositories = load_repositories(args.input_json)
    emit_yaml(repositories, output=sys.stdout)


if __name__ == "__main__":
    main()
