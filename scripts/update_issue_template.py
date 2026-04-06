#!/usr/bin/env python3
"""Update the GitHub Pages admin enablement issue template in-place."""
from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Tuple

STATE_PATH = Path("data/pages_blocked_state.json")
TEMPLATE_PATH = Path(".github/ISSUE_TEMPLATE/github-pages-admin-enablement.md")
REPORT_PATH = Path("docs/admin_notification.md")
PLACEHOLDER = "[automation will pre-fill affected repositories]"


def load_state(path: Path = STATE_PATH) -> Tuple[List[str], str | None]:
    """Return blocked repositories and an ISO date derived from the JSON timestamp."""
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)

    repos = data.get("blocked_repositories")
    if not isinstance(repos, list):
        raise ValueError("blocked_repositories is missing or not a list")

    timestamp = data.get("timestamp")
    report_date: str | None = None
    if isinstance(timestamp, str):
        try:
            report_date = (
                datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                .date()
                .isoformat()
            )
        except ValueError:
            report_date = None

    return [str(repo) for repo in repos], report_date


def build_checkbox_lines(repositories: Iterable[str], indent: str) -> List[str]:
    """Construct YAML checkbox lines honoring the existing indentation."""
    lines: List[str] = []
    for repo in repositories:
        label = json.dumps(repo)
        lines.append(f"{indent}- label: {label}")
        lines.append(f"{indent}  required: false")
    return lines


def replace_placeholder_block(lines: List[str], repositories: List[str]) -> List[str]:
    """Replace the placeholder option with the list of repository checkboxes."""
    try:
        placeholder_index = next(
            idx for idx, line in enumerate(lines) if PLACEHOLDER in line
        )
    except StopIteration as exc:
        raise ValueError("Placeholder text not found in issue template") from exc

    if placeholder_index + 1 >= len(lines):
        raise ValueError("Placeholder block is incomplete (missing required line)")

    indent = lines[placeholder_index].split("- label", 1)[0]
    checkbox_lines = build_checkbox_lines(repositories, indent)

    # Drop the placeholder label and its required line, then insert the new block.
    return (
        lines[:placeholder_index]
        + checkbox_lines
        + lines[placeholder_index + 2 :]
    )


def build_report_link(report_date: str | None) -> str:
    """Create a Markdown link to the latest report with a dated label if available."""
    relative_path = Path(
        os.path.relpath(REPORT_PATH, TEMPLATE_PATH.parent)
    ).as_posix()
    label = f"{report_date} report" if report_date else "latest report"
    return f"[{label}]({relative_path})"


def update_report_line(lines: List[str], link: str) -> List[str]:
    """Swap the '[link]' placeholder with a concrete Markdown link."""
    for idx, line in enumerate(lines):
        if "See latest report:" in line:
            prefix = line.split("See latest report:", 1)[0] + "See latest report: "
            lines[idx] = f"{prefix}{link}"
            return lines
    raise ValueError("Could not find the 'See latest report' line in the template")


def write_template(lines: List[str]) -> None:
    """Write the updated template back to disk with a trailing newline."""
    TEMPLATE_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    repositories, report_date = load_state()
    template_lines = TEMPLATE_PATH.read_text(encoding="utf-8").splitlines()

    updated_lines = replace_placeholder_block(template_lines, repositories)
    link = build_report_link(report_date)
    updated_lines = update_report_line(updated_lines, link)

    write_template(updated_lines)
    print(
        f"Updated {TEMPLATE_PATH} with {len(repositories)} repositories and link "
        f"to {REPORT_PATH}."
    )


if __name__ == "__main__":
    main()
