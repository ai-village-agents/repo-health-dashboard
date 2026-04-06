import re

with open('docs/github_pages_admin_bottleneck.md', 'r') as f:
    content = f.read()

# Update blocked repositories section
new_blocked_section = """## Blocked Repositories (3)

The following repositories are currently **admin‑blocked** (GitHub Pages not enabled):

- `ai‑village‑agents/gpt5‑breaking‑news` — PR #4 (`restore-pages-source`) **open**, ready for merge; Pages needs admin enablement after merge.
- `ai‑village‑agents/village‑operations‑handbook` — PR #6 (`add-pages-source`) **merged**; source files on `main`; Pages needs admin enablement.
- `ai‑village‑agents/lessons‑from‑293‑days` — source files **already on `main`** (merged); Pages needs admin enablement.

## Live Repositories (29)"""

# Find the start of blocked repos section and replace until "## Live Repositories"
pattern = r'## Blocked Repositories \(3\)[\s\S]*?## Live Repositories'
updated = re.sub(pattern, new_blocked_section, content)

# Update Next Steps section
new_next_steps = """## Next Steps

- **Immediate admin action needed:** Enable GitHub Pages via **Settings → Pages** for all three blocked repositories:
  1. `gpt5-breaking-news` (after PR #4 merge)
  2. `village-operations-handbook` (ready now)
  3. `lessons-from-293-days` (ready now)
- Merge PR #4 (`restore-pages-source`) for `gpt5-breaking-news`.
- Re-run the `pages_check.py` scanner to confirm **32/32** live sites once enablement is complete."""

# Find Next Steps section
next_steps_pattern = r'## Next Steps[\s\S]*?## Future Steps'
updated = re.sub(next_steps_pattern, new_next_steps, updated)

# Update last updated timestamp
updated = re.sub(r'Last updated: \d{4}‑\d{2}‑\d{2}', f'Last updated: 2026‑02‑18', updated)

with open('docs/github_pages_admin_bottleneck.md', 'w') as f:
    f.write(updated)

print("Updated bottleneck documentation")
