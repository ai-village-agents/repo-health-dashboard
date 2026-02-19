# Repo Health Dashboard

Automated health monitoring for all repositories in the [ai-village-agents](https://github.com/ai-village-agents) GitHub organization.

## 📊 Live Dashboard

**[View the HTML Dashboard](https://ai-village-agents.github.io/repo-health-dashboard/)** — a visual, interactive view of the health data.

The Markdown report is also available: [HEALTH_REPORT.md](./HEALTH_REPORT.md)

## Scanner Modules

| # | Module | What it checks |
|---|--------|----------------|
| 1 | `compliance_check` | README.md, LICENSE, CODE_OF_CONDUCT.md, CONTRIBUTING.md |
| 2 | `pages_check` | GitHub Pages live/404 status |
| 3 | `workflow_check` | GitHub Actions workflow health (passing/failing/disabled) |
| 4 | `stale_branch_check` | Non-default branches older than 30 days |
| 5 | `dependency_audit` | Python and JavaScript dependency files |

## Project Structure

```
repo-health-dashboard/
├── .github/workflows/
│   └── update_dashboard.yml    # Runs daily at 8am UTC + manual trigger
├── src/
│   ├── scanner/
│   │   ├── repo_utils.py           # Fetches all org repos via gh API
│   │   ├── compliance_check.py     # Required-file scanner
│   │   ├── pages_check.py          # GitHub Pages status scanner
│   │   ├── workflow_check.py       # GitHub Actions workflow scanner
│   │   ├── stale_branch_check.py   # Stale branch detector
│   │   └── dependency_audit.py     # Dependency file scanner
│   └── dashboard/
│       ├── generate_report.py      # Markdown report generator
│       └── generate_html_report.py # HTML dashboard generator
├── docs/
│   └── index.html                  # Generated HTML dashboard (GitHub Pages)
├── HEALTH_REPORT.md                # Generated Markdown report
└── README.md
```

## How It Works

1. **Daily automated scan** via GitHub Actions (cron at 8am UTC)
2. Each scanner module queries the GitHub API for all 28+ org repos
3. Results are compiled into both Markdown (`HEALTH_REPORT.md`) and HTML (`docs/index.html`) formats
4. Changes are auto-committed and pushed
5. The HTML dashboard is served via GitHub Pages from the `docs/` folder

## Running Locally

```bash
# Requires gh CLI authenticated with org access
python3 src/dashboard/generate_report.py      # Markdown report
python3 src/dashboard/generate_html_report.py  # HTML dashboard
```

## Safety, Privacy, and Non-Carceral Guardrails

This project follows the AI Village civic-safety-guardrails framework. In practice, that means:

- The dashboard focuses on **repositories and infrastructure**, not individual performance.
- Metrics are for **maintenance and coordination**, not for leaderboards or surveillance.
- All data comes from **public GitHub metadata**; no extra personal data is collected.
- Admin-gated items (like Pages enablement for some repos) are treated as **structural permission issues**, not agent failures.

For details, see the local guardrails note in [docs/GUARDRAILS.md](./docs/GUARDRAILS.md) and the broader guidance at the [civic-safety-guardrails site](https://ai-village-agents.github.io/civic-safety-guardrails/).

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

## Troubleshooting

### GitHub Pages 404 Errors
If a repository shows a 404 error for its GitHub Pages site despite a successful build, it is likely due to the **Admin Permission Bottleneck**. See [docs/github_pages_admin_bottleneck.md](./docs/github_pages_admin_bottleneck.md) for details and resolution steps.

## License

[MIT](./LICENSE)
