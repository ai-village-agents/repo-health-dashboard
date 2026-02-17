"""Workflow Health Scanner — checks GitHub Actions workflow status across all org repos.

Scans each repository for:
- Number of workflows defined
- Status of each workflow (passing ✅ / failing ❌ / no runs ⚪ / disabled 🚫)
- Last run date and conclusion
"""

import subprocess
import json
from datetime import datetime, timezone

try:
    from .repo_utils import get_all_repos
except ImportError:
    import os, sys
    if __package__ is None or __package__ == '':
        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        if repo_root not in sys.path:
            sys.path.insert(0, repo_root)
        from src.scanner.repo_utils import get_all_repos
    else:
        raise


def _run_gh(cmd):
    """Run a gh CLI command and return (stdout, returncode)."""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip(), result.returncode


def get_workflows(repo):
    """List all workflow files defined in a repo."""
    stdout, rc = _run_gh(f"gh api repos/{repo}/actions/workflows --paginate")
    if rc != 0:
        return []
    try:
        data = json.loads(stdout)
        return data.get("workflows", [])
    except json.JSONDecodeError:
        return []


def get_latest_run(repo, workflow_id):
    """Get the most recent run for a given workflow."""
    stdout, rc = _run_gh(
        f"gh api 'repos/{repo}/actions/workflows/{workflow_id}/runs?per_page=1'"
    )
    if rc != 0:
        return None
    try:
        data = json.loads(stdout)
        runs = data.get("workflow_runs", [])
        return runs[0] if runs else None
    except (json.JSONDecodeError, IndexError):
        return None


def classify_workflow(workflow, latest_run):
    """Classify a workflow's health status.
    
    Returns a dict with:
      - status_icon: emoji indicator
      - status_text: human-readable status
      - conclusion: last run conclusion (or N/A)
      - last_run_date: ISO date of last run (or N/A)
      - days_since_run: integer days since last run (or None)
    """
    # Check if workflow is disabled
    if workflow.get("state") == "disabled_manually":
        return {
            "status_icon": "🚫",
            "status_text": "Disabled",
            "conclusion": "N/A",
            "last_run_date": "N/A",
            "days_since_run": None,
        }

    if latest_run is None:
        return {
            "status_icon": "⚪",
            "status_text": "No runs",
            "conclusion": "N/A",
            "last_run_date": "N/A",
            "days_since_run": None,
        }

    conclusion = latest_run.get("conclusion") or latest_run.get("status", "unknown")
    run_date_str = latest_run.get("created_at", "")
    
    # Parse date
    last_run_date = "N/A"
    days_since = None
    if run_date_str:
        try:
            run_dt = datetime.fromisoformat(run_date_str.replace("Z", "+00:00"))
            last_run_date = run_dt.strftime("%Y-%m-%d")
            days_since = (datetime.now(timezone.utc) - run_dt).days
        except ValueError:
            pass

    if conclusion == "success":
        icon, text = "✅", "Passing"
    elif conclusion == "failure":
        icon, text = "❌", "Failing"
    elif conclusion == "cancelled":
        icon, text = "⏹️", "Cancelled"
    elif conclusion in ("in_progress", "queued", "waiting", "pending"):
        icon, text = "🔄", "In Progress"
    elif conclusion == "skipped":
        icon, text = "⏭️", "Skipped"
    else:
        icon, text = "⚠️", f"Unknown ({conclusion})"

    return {
        "status_icon": icon,
        "status_text": text,
        "conclusion": conclusion,
        "last_run_date": last_run_date,
        "days_since_run": days_since,
    }


def scan_workflow_health():
    """Scan all repos for workflow health. Returns structured results."""
    repos = get_all_repos()
    print(f"Scanning workflow health for {len(repos)} repositories...\n")

    results = {}
    
    # Summary counters
    total_workflows = 0
    passing = 0
    failing = 0
    disabled = 0
    no_runs = 0
    other = 0

    for repo in repos:
        workflows = get_workflows(repo)
        repo_results = []

        if not workflows:
            results[repo] = []
            continue

        for wf in workflows:
            wf_id = wf["id"]
            wf_name = wf.get("name", wf.get("path", "unknown"))
            wf_path = wf.get("path", "")

            latest_run = get_latest_run(repo, wf_id)
            classification = classify_workflow(wf, latest_run)

            total_workflows += 1
            st = classification["status_text"]
            if st == "Passing":
                passing += 1
            elif st == "Failing":
                failing += 1
            elif st == "Disabled":
                disabled += 1
            elif st == "No runs":
                no_runs += 1
            else:
                other += 1

            repo_results.append({
                "name": wf_name,
                "path": wf_path,
                **classification,
            })

            # Print live progress
            icon = classification["status_icon"]
            date = classification["last_run_date"]
            print(f"  {repo:<40} | {wf_name:<30} | {icon} {classification['status_text']:<12} | {date}")

        results[repo] = repo_results

    print(f"\n--- Workflow Health Summary ---")
    print(f"Total workflows: {total_workflows}")
    print(f"  ✅ Passing:    {passing}")
    print(f"  ❌ Failing:    {failing}")
    print(f"  🚫 Disabled:   {disabled}")
    print(f"  ⚪ No runs:    {no_runs}")
    print(f"  ⚠️  Other:      {other}")

    return results


if __name__ == "__main__":
    print("\n--- WORKFLOW HEALTH SCAN ---\n")
    scan_workflow_health()
