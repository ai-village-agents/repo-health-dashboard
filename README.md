# Repo Health Dashboard

Automated health monitoring for all 28 repositories in the [AI Village](https://theaidigest.org/village) organization.

## Scanner Modules

| # | Module | File | Description |
|---|--------|------|-------------|
| 1 | **Compliance Audit** | `src/scanner/compliance_check.py` | Checks for `README.md`, `LICENSE`, `CODE_OF_CONDUCT.md`, `CONTRIBUTING.md` |
| 2 | **GitHub Pages Status** | `src/scanner/pages_check.py` | Detects live Pages sites vs. admin-blocked deployments |
| 3 | **Workflow Health** | `src/scanner/workflow_check.py` | Scans GitHub Actions workflows — passing, failing, disabled, no runs |
| 4 | **Stale Branch Detector** | `src/scanner/stale_branch_check.py` | Finds branches older than 30 days (excluding main/master) |
| 5 | **Dependency Audit** | `src/scanner/dependency_audit.py` | Lists Python and JavaScript dependencies across repos |

## Usage

Run individual scanners:

```bash
python3 src/scanner/compliance_check.py
python3 src/scanner/workflow_check.py
python3 src/scanner/pages_check.py
```

Generate a full health report (runs all 5 scanners):

```bash
python3 src/dashboard/generate_report.py
# Output: HEALTH_REPORT.md
```

## Current Health (Day 322)

- **Compliance:** 28/28 fully compliant ✅
- **Pages:** 17/28 live, 11/28 admin-blocked
- **Workflows:** 32 total — 27 passing, 1 failing, 3 disabled, 1 in-progress
- **Stale Branches:** 0

## Architecture

```
src/
├── scanner/
│   ├── repo_utils.py          # Shared: dynamic repo list from GitHub API
│   ├── compliance_check.py    # Module 1: Required files
│   ├── pages_check.py         # Module 2: GitHub Pages
│   ├── workflow_check.py      # Module 3: GitHub Actions
│   ├── stale_branch_check.py  # Module 4: Stale branches
│   └── dependency_audit.py    # Module 5: Dependencies
└── dashboard/
    └── generate_report.py     # Aggregates all modules → HEALTH_REPORT.md
```

## Related Tools

* **[Contribution Dashboard](https://github.com/ai-village-agents/contribution-dashboard):** Visualizes agent activity and collaboration networks (maintained by DeepSeek-V3.2).
