import re

with open('docs/github_pages_admin_bottleneck.md', 'r') as f:
    content = f.read()

# Update blocked repositories section
new_blocked_section = """## Blocked Repositories (3)

The following repositories are currently **admin‑blocked** (GitHub Pages not enabled):

- `ai‑village‑agents/gpt5‑breaking‑news` — PR #4 (`restore-pages-source`) **merged**; source files on `main`; Pages needs admin enablement now.
- `ai‑village‑agents/village‑operations‑handbook` — PR #6 (`add-pages-source`) **merged**; source files on `main`; Pages needs admin enablement now.
- `ai‑village‑agents/lessons‑from‑293‑days` — source files **on `main`** (merged); Pages needs admin enablement now.

## Live Repositories (29)"""

# Find the start of blocked repos section and replace until "## Live Repositories"
pattern = r'## Blocked Repositories \(3\)[\s\S]*?## Live Repositories'
content = re.sub(pattern, new_blocked_section, content)

# Update Next Steps section
new_next_steps = """## Next Steps

- **Immediate admin action needed:** Enable GitHub Pages via **Settings → Pages** for all three repositories:
  1. `gpt5-breaking-news` (ready now)
  2. `village-operations-handbook` (ready now)
  3. `lessons-from-293-days` (ready now)
- Re-run the `pages_check.py` scanner to confirm **32/32** live sites once enablement is complete."""

next_steps_pattern = r'## Next Steps[\s\S]*?## Future Steps'
content = re.sub(next_steps_pattern, new_next_steps, content)

with open('docs/github_pages_admin_bottleneck.md', 'w') as f:
    f.write(content)

print("Updated bottleneck documentation with PR #4 merged status")
