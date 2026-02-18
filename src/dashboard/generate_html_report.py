"""Generate an interactive HTML dashboard for AI Village repo health.

This module reads the same scanner data as generate_report.py and produces
a self-contained HTML file (docs/index.html) suitable for GitHub Pages.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.scanner.compliance_check import REMEDIATION_STEPS, scan_repos
from src.scanner.stale_branch_check import scan_stale_branches
from src.scanner.dependency_audit import audit_dependencies
from src.scanner.pages_check import scan_pages_status
from src.scanner.workflow_check import scan_workflow_health
from src.scanner.activity_check import scan_open_prs, scan_open_issues, scan_non_default_branches
from src.scanner.shadowban_check import check_shadowbans
from datetime import datetime
import html as html_mod


def _esc(text):
    """Escape HTML entities."""
    return html_mod.escape(str(text))


def generate_html_report():
    print("Running compliance scan...")
    compliance_results = scan_repos()

    print("Running stale branch scan...")
    stale_results = scan_stale_branches()

    print("Running dependency audit...")
    dependency_results = audit_dependencies()

    print("Running Pages status scan...")
    pages_results = scan_pages_status()

    print("Running workflow health scan...")
    workflow_results = scan_workflow_health()

    print('Running open PRs scan...')
    open_prs = scan_open_prs()
    print('Running open issues scan...')
    open_issues = scan_open_issues()
    print('Running non-default branches scan...')
    non_default_branches = scan_non_default_branches()
    print('Running shadowban check...')
    shadowban_results = check_shadowbans()

    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    total_repos = len(compliance_results)
    fully_compliant = sum(
        1 for s in compliance_results.values()
        if s.get('README.md') and s.get('LICENSE')
        and s.get('CODE_OF_CONDUCT.md') and s.get('CONTRIBUTING.md')
    )

    pages_live = sum(1 for v in pages_results.values() if '✅' in str(v) or 'Live' in str(v))

    wf_total = wf_pass = wf_fail = wf_dis = 0
    for wfs in workflow_results.values():
        for wf in (wfs or []):
            wf_total += 1
            st = wf["status_text"]
            if st == "Passing": wf_pass += 1
            elif st == "Failing": wf_fail += 1
            elif st == "Disabled": wf_dis += 1

    stale_count = sum(len(branches) for branches in stale_results.values())
    pr_count = len(open_prs)
    issue_count = len(open_issues)

    # --- Build HTML ---
    compliance_rows = []
    for repo, status in sorted(compliance_results.items()):
        short = repo.split('/')[-1]
        cells = []
        for f in ['README.md', 'LICENSE', 'CODE_OF_CONDUCT.md', 'CONTRIBUTING.md']:
            ok = status.get(f, False)
            cells.append(f'<td class="{"pass" if ok else "fail"}">{"&#10003;" if ok else "&#10007;"}</td>')
        all_ok = all(status.get(f) for f in ['README.md', 'LICENSE', 'CODE_OF_CONDUCT.md', 'CONTRIBUTING.md'])
        row_class = 'row-pass' if all_ok else 'row-warn'
        compliance_rows.append(
            f'<tr class="{row_class}"><td><a href="https://github.com/{_esc(repo)}" target="_blank">{_esc(short)}</a></td>'
            + ''.join(cells) + '</tr>'
        )

    pages_rows = []
    for repo, status in sorted(pages_results.items()):
        short = repo.split('/')[-1]
        is_live = '✅' in str(status) or 'Live' in str(status)
        cls = 'pass' if is_live else 'neutral'
        pages_rows.append(
            f'<tr><td><a href="https://github.com/{_esc(repo)}" target="_blank">{_esc(short)}</a></td>'
            f'<td class="{cls}">{_esc(status)}</td></tr>'
        )

    wf_rows = []
    for repo, wfs in sorted(workflow_results.items()):
        if not wfs:
            continue
        short = repo.split('/')[-1]
        for wf in wfs:
            icon = _esc(wf['status_icon'])
            txt = _esc(wf['status_text'])
            cls = 'pass' if wf['status_text'] == 'Passing' else ('fail' if wf['status_text'] == 'Failing' else 'neutral')
            wf_rows.append(
                f'<tr><td><a href="https://github.com/{_esc(repo)}" target="_blank">{_esc(short)}</a></td>'
                f'<td>{_esc(wf["name"])}</td>'
                f'<td class="{cls}">{icon} {txt}</td>'
                f'<td>{_esc(wf["last_run_date"])}</td></tr>'
            )

    stale_rows = []
    for repo, branches in sorted(stale_results.items()):
        short = repo.split('/')[-1]
        for b in branches:
            stale_rows.append(
                f'<tr><td>{_esc(short)}</td><td>{_esc(b["name"])}</td>'
                f'<td>{_esc(b["date"])}</td><td>{_esc(b["age"])} days</td></tr>'
            )

    pr_rows = []
    for pr in open_prs:
        pr_rows.append(
            f'<tr><td><a href="https://github.com/ai-village-agents/{_esc(pr["repo"])}" target="_blank">{_esc(pr["repo"])}</a></td>'
            f'<td><a href="{_esc(pr["url"])}" target="_blank">#{pr["number"]}: {_esc(pr["title"])}</a></td>'
            f'<td>{_esc(pr["author"])}</td>'
            f'<td>{_esc(pr["created"])}</td></tr>'
        )

    issue_rows = []
    for issue in open_issues:
        issue_rows.append(
            f'<tr><td><a href="https://github.com/ai-village-agents/{_esc(issue["repo"])}" target="_blank">{_esc(issue["repo"])}</a></td>'
            f'<td><a href="{_esc(issue["url"])}" target="_blank">#{issue["number"]}: {_esc(issue["title"])}</a></td>'
            f'<td>{_esc(issue["author"])}</td>'
            f'<td>{_esc(issue["created"])}</td></tr>'
        )

    branch_info_rows = []
    for repo_name, branches in sorted(non_default_branches.items()):
        for br in branches:
            branch_info_rows.append(
                f'<tr><td><a href="https://github.com/ai-village-agents/{_esc(repo_name)}" target="_blank">{_esc(repo_name)}</a></td>'
                f'<td>{_esc(br)}</td></tr>'
            )

    dep_sections = []
    for repo, deps in sorted(dependency_results.items()):
        if not deps.get('python') and not deps.get('javascript'):
            continue
        short = repo.split('/')[-1]
        items = []
        for d in (deps.get('python') or []):
            items.append(f'<span class="dep-badge python">{_esc(d)}</span>')
        for d in (deps.get('javascript') or []):
            items.append(f'<span class="dep-badge js">{_esc(d)}</span>')
        dep_sections.append(f'<div class="dep-repo"><strong>{_esc(short)}</strong>: {" ".join(items)}</div>')

    remediation_targets = {}
    for repo, status in compliance_results.items():
        missing_files = [fname for fname, present in status.items() if not present]
        if missing_files:
            remediation_targets[repo] = missing_files

    compliance_remediation_html = '<div class="empty">All repositories have the required compliance files.</div>'
    if remediation_targets:
        remediation_blocks = []
        for repo, missing_files in sorted(remediation_targets.items()):
            repo_dir = repo.split('/')[-1]
            repo_link = f'<a href="https://github.com/{_esc(repo)}" target="_blank">{_esc(repo)}</a>'
            steps = []
            for fname in missing_files:
                template = REMEDIATION_STEPS.get(fname)
                instruction = template.format(repo=repo, repo_dir=repo_dir) if template else f"Add {fname} to the repository and push the change."
                steps.append(f'<li><strong>{_esc(fname)}</strong>: <code>{_esc(instruction)}</code></li>')
            remediation_blocks.append(f'<div class="remediation-repo"><div class="repo-name">{repo_link}</div><ul>' + ''.join(steps) + '</ul></div>')
        compliance_remediation_html = ''.join(remediation_blocks)

    failing_workflow_targets = {}
    for repo, workflows in workflow_results.items():
        for wf in (workflows or []):
            if wf.get('status_text') == 'Failing':
                failing_workflow_targets.setdefault(repo, []).append(wf.get('name'))

    failing_workflows_html = '<div class="empty">No failing workflows detected.</div>'
    if failing_workflow_targets:
        failing_blocks = []
        for repo, workflow_names in sorted(failing_workflow_targets.items()):
            repo_link = f'<a href="https://github.com/{_esc(repo)}" target="_blank">{_esc(repo)}</a>'
            commands = ''.join(
                f'<li><strong>{_esc(name)}</strong>: <code>gh run list --workflow "{_esc(name)}" --repo {_esc(repo)}</code></li>'
                for name in sorted(workflow_names)
            )
            failing_blocks.append(f'<div class="remediation-repo"><div class="repo-name">{repo_link}</div><ul>{commands}</ul></div>')
        failing_workflows_html = ''.join(failing_blocks)

    admin_blocked_pages = [
        repo for repo, status in pages_results.items()
        if isinstance(status, str) and status.startswith("🚫 Admin Blocked")
    ]
    admin_blocked_html = '<div class="empty">No admin-blocked Pages sites detected.</div>'
    if admin_blocked_pages:
        admin_list = ''.join(
            f'<li><a href="https://github.com/{_esc(repo)}" target="_blank">{_esc(repo)}</a></li>'
            for repo in sorted(admin_blocked_pages)
        )
        admin_blocked_html = '<p>Email <code>help@agentvillage.org</code> to request Pages enablement for:</p><ul>' + admin_list + '</ul>'

    shadowbanned_agents = [
        agent for agent, data in shadowban_results.items()
        if data.get("status") == 404
    ]
    shadowban_html = '<div class="empty">No shadowbanned agents detected.</div>'
    if shadowbanned_agents:
        shadowban_list = ''.join(f'<li><code>{_esc(agent)}</code></li>' for agent in sorted(shadowbanned_agents))
        shadowban_html = '<p>Use git CLI, avoid web UI for these agents until visibility is restored:</p><ul>' + shadowban_list + '</ul>'

    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AI Village — Repo Health Dashboard</title>
<style>
:root {{
  --green: #2e7d32;
  --green-light: #e8f5e9;
  --red: #c62828;
  --red-light: #ffebee;
  --blue: #1565c0;
  --gray: #f5f5f5;
  --gray-mid: #666;
  --white: #fff;
  --shadow: 0 2px 8px rgba(0,0,0,0.08);
}}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: #f0f2f5; color: #333; line-height: 1.6;
}}
.header {{
  background: linear-gradient(135deg, #1a237e, #283593);
  color: var(--white); padding: 2rem; text-align: center;
}}
.header h1 {{ font-size: 2rem; margin-bottom: 0.5rem; }}
.header p {{ opacity: 0.85; font-size: 0.95rem; }}
.cards {{
  display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 1rem; max-width: 900px; margin: -1.5rem auto 1.5rem; padding: 0 1rem;
  position: relative; z-index: 1;
}}
.card {{
  background: var(--white); border-radius: 12px; padding: 1.2rem 1rem;
  box-shadow: var(--shadow); text-align: center;
}}
.card .number {{ font-size: 2rem; font-weight: 700; }}
.card .label {{ font-size: 0.85rem; color: var(--gray-mid); margin-top: 0.25rem; }}
.card.green .number {{ color: var(--green); }}
.card.red .number {{ color: var(--red); }}
.card.blue .number {{ color: var(--blue); }}
.container {{ max-width: 1100px; margin: 0 auto; padding: 0 1rem 2rem; }}
.section {{
  background: var(--white); border-radius: 12px; padding: 1.5rem;
  margin-bottom: 1.5rem; box-shadow: var(--shadow);
}}
.section h2 {{
  font-size: 1.25rem; margin-bottom: 1rem;
  padding-bottom: 0.5rem; border-bottom: 2px solid var(--gray);
}}
table {{ width: 100%; border-collapse: collapse; font-size: 0.9rem; }}
th {{ text-align: left; padding: 0.6rem 0.5rem; background: var(--gray); font-weight: 600; }}
td {{ padding: 0.5rem; border-bottom: 1px solid #eee; }}
td a {{ color: var(--blue); text-decoration: none; }}
td a:hover {{ text-decoration: underline; }}
.pass {{ color: var(--green); font-weight: 600; }}
.fail {{ color: var(--red); font-weight: 600; }}
.neutral {{ color: var(--gray-mid); }}
.row-pass {{ background: var(--green-light); }}
.row-warn {{ background: var(--red-light); }}
.dep-badge {{
  display: inline-block; padding: 0.15rem 0.5rem; border-radius: 10px;
  font-size: 0.8rem; margin: 0.15rem;
}}
.dep-badge.python {{ background: #e3f2fd; color: #1565c0; }}
.dep-badge.js {{ background: #fff3e0; color: #e65100; }}
.dep-repo {{ margin-bottom: 0.5rem; }}
.empty {{ text-align: center; padding: 2rem; color: var(--green); font-weight: 600; font-size: 1.1rem; }}
.section h3 {{ margin: 0.5rem 0 0.35rem; font-size: 1rem; }}
ul {{ margin: 0.25rem 0 0.75rem 1.25rem; }}
.remediation-repo {{ margin-bottom: 1rem; }}
.remediation-repo .repo-name {{ font-weight: 600; margin-bottom: 0.25rem; }}
.footer {{
  text-align: center; padding: 1.5rem; color: var(--gray-mid); font-size: 0.85rem;
}}
.footer a {{ color: var(--blue); }}
</style>
</head>
<body>
<div class="header">
  <h1>&#x1F3E5; AI Village — Repo Health Dashboard</h1>
  <p>Automated health scan of all {total_repos} repositories in the ai-village-agents organization</p>
  <p>Last updated: {_esc(now)}</p>
</div>

<div class="cards">
  <div class="card green">
    <div class="number">{fully_compliant}/{total_repos}</div>
    <div class="label">Repos Compliant</div>
  </div>
  <div class="card blue">
    <div class="number">{pages_live}</div>
    <div class="label">Pages Live</div>
  </div>
  <div class="card green">
    <div class="number">{wf_pass}/{wf_total}</div>
    <div class="label">Workflows Passing</div>
  </div>
  <div class="card {"green" if stale_count == 0 else "red"}">
    <div class="number">{stale_count}</div>
    <div class="label">Stale Branches</div>
  </div>
  <div class="card {"green" if pr_count == 0 else "blue"}">
    <div class="number">{pr_count}</div>
    <div class="label">Open PRs</div>
  </div>
  <div class="card blue">
    <div class="number">{issue_count}</div>
    <div class="label">Open Issues</div>
  </div>
</div>

<div class="container">

<div class="section">
<h2>1. Compliance Audit</h2>
<p style="margin-bottom:1rem;color:var(--gray-mid);font-size:0.9rem;">
  Checks for README.md, LICENSE, CODE_OF_CONDUCT.md, and CONTRIBUTING.md in each repo.
</p>
<table>
<tr><th>Repository</th><th>README</th><th>LICENSE</th><th>CoC</th><th>CONTRIBUTING</th></tr>
{''.join(compliance_rows)}
</table>
</div>

<div class="section">
<h2>2. Deployment Status (GitHub Pages)</h2>
<table>
<tr><th>Repository</th><th>Status</th></tr>
{''.join(pages_rows)}
</table>
</div>

<div class="section">
<h2>3. Workflow Health</h2>
<table>
<tr><th>Repository</th><th>Workflow</th><th>Status</th><th>Last Run</th></tr>
{''.join(wf_rows)}
</table>
<p style="margin-top:1rem;color:var(--gray-mid);font-size:0.9rem;">
  Total: {wf_total} workflows &mdash; {wf_pass} passing, {wf_fail} failing, {wf_dis} disabled
</p>
</div>

<div class="section">
<h2>4. Stale Branches</h2>
{'<div class="empty">&#10003; No stale branches found &mdash; the ecosystem is clean!</div>' if not stale_rows else
'<table><tr><th>Repository</th><th>Branch</th><th>Last Commit</th><th>Age</th></tr>' + ''.join(stale_rows) + '</table>'}
</div>

<div class="section">
<h2>5. Dependencies</h2>
{''.join(dep_sections) if dep_sections else '<div class="empty">No external dependencies detected.</div>'}
</div>

<div class="section">
<h2>6. Open Pull Requests</h2>
{'<div class="empty">&#10003; No open pull requests &mdash; all caught up!</div>' if not pr_rows else
'<table><tr><th>Repository</th><th>Pull Request</th><th>Author</th><th>Opened</th></tr>' + ''.join(pr_rows) + '</table>'}
</div>

<div class="section">
<h2>7. Open Issues</h2>
{'<div class="empty">No open issues!</div>' if not issue_rows else
'<table><tr><th>Repository</th><th>Issue</th><th>Author</th><th>Opened</th></tr>' + ''.join(issue_rows) + '</table>'}
</div>

<div class="section">
<h2>8. Active Branches</h2>
{'<div class="empty">&#10003; Only default branches &mdash; ecosystem is clean!</div>' if not branch_info_rows else
'<table><tr><th>Repository</th><th>Branch</th></tr>' + ''.join(branch_info_rows) + '</table>'}
</div>

<div class="section">
<h2>10. Remediation Plan</h2>
<p style="margin-bottom:1rem;color:var(--gray-mid);font-size:0.9rem;">
  Actionable steps to add missing compliance files and unblock access issues.
</p>
<h3>Compliance files</h3>
{compliance_remediation_html}

<h3>Failing Workflows</h3>
{failing_workflows_html}

<h3>Admin Blocked Pages</h3>
{admin_blocked_html}

<h3>Shadowbanned agents</h3>
{shadowban_html}
</div>

</div>

<div class="footer">
  <p>Powered by <a href="https://github.com/ai-village-agents/repo-health-dashboard">repo-health-dashboard</a>
  &middot; Part of <a href="https://theaidigest.org/village">AI Village</a></p>
</div>
</body>
</html>"""

    os.makedirs("docs", exist_ok=True)
    with open("docs/index.html", "w") as f:
        f.write(page)
    print("\nHTML dashboard generated: docs/index.html")


if __name__ == "__main__":
    generate_html_report()
