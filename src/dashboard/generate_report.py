"""
Fixed dashboard report generator with parallel scanning and timeouts.
"""
import sys
import os
import concurrent.futures
import time
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# Try to import parallel versions, fall back to original
try:
    from src.scanner.compliance_check_parallel import scan_repos as scan_repos_parallel
    use_parallel_compliance = True
    print("✓ Using parallel compliance scanner")
except ImportError:
    from src.scanner.compliance_check import scan_repos as scan_repos_parallel
    use_parallel_compliance = False
    print("⚠ Using original compliance scanner (parallel not available)")

try:
    from src.scanner.stale_branch_check_parallel import scan_stale_branches as scan_stale_branches_parallel
    use_parallel_stale = True
    print("✓ Using parallel stale branch scanner")
except ImportError:
    from src.scanner.stale_branch_check import scan_stale_branches as scan_stale_branches_parallel
    use_parallel_stale = False
    print("⚠ Using original stale branch scanner (parallel not available)")

# Import other scanners
from src.scanner.dependency_audit import audit_dependencies
from src.scanner.pages_check import scan_pages_status
from src.scanner.workflow_check import scan_workflow_health
from src.scanner.activity_check import scan_open_prs, scan_open_issues, scan_non_default_branches
from src.scanner.shadowban_check import check_shadowbans

def run_scan_with_timeout(func, name, timeout=300, default=None):
    """Run a scan function with timeout using ThreadPoolExecutor."""
    print(f"\n[START] {name}")
    start_time = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(func)
        try:
            result = future.result(timeout=timeout)
            elapsed = time.time() - start_time
            print(f"[DONE] {name} completed in {elapsed:.2f} seconds")
            return result
        except concurrent.futures.TimeoutError:
            elapsed = time.time() - start_time
            print(f"[TIMEOUT] {name} timed out after {elapsed:.2f} seconds")
            return default
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"[ERROR] {name} failed after {elapsed:.2f} seconds: {e}")
            return default

def generate_markdown_report_fixed():
    """Generate health report using parallel scanning with timeouts."""
    print("=" * 70)
    print("AI Village Repository Health Report - Fixed Generator")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print(f"Parallel compliance: {'✅' if use_parallel_compliance else '❌'}")
    print(f"Parallel stale branches: {'✅' if use_parallel_stale else '❌'}")
    print("=" * 70)
    
    overall_start = time.time()
    
    # Define scans with appropriate timeouts (in seconds)
    scans = [
        ("compliance scan", scan_repos_parallel, 300),      # 5 minutes
        ("stale branch scan", scan_stale_branches_parallel, 300),  # 5 minutes
        ("dependency audit", audit_dependencies, 180),       # 3 minutes
        ("Pages status scan", scan_pages_status, 180),       # 3 minutes
        ("workflow health scan", scan_workflow_health, 240), # 4 minutes
        ("open PRs scan", scan_open_prs, 120),               # 2 minutes
        ("open issues scan", scan_open_issues, 180),         # 3 minutes
        ("non-default branches scan", scan_non_default_branches, 180), # 3 minutes
        ("shadowban check", check_shadowbans, 120),          # 2 minutes
    ]
    
    results = {}
    
    # Run scans sequentially to avoid GitHub API rate limiting
    # Each scan can be parallel internally
    for name, func, timeout_val in scans:
        results[name] = run_scan_with_timeout(func, name, timeout_val, {})
    
    elapsed_total = time.time() - overall_start
    print(f"\n{'='*70}")
    print(f"All scans completed in {elapsed_total:.2f} seconds ({elapsed_total/60:.1f} minutes)")
    
    # Generate report
    report = generate_report_markdown(results, elapsed_total)
    
    # Write report
    with open("HEALTH_REPORT.md", "w") as f:
        f.write(report)
    
    print(f"\nFixed report generated: HEALTH_REPORT.md")
    print(f"Report length: {len(report)} characters")
    
    return report

def generate_report_markdown(results, elapsed_total):
    """Generate markdown report from scan results."""
    report = f"# AI Village Repository Health Report\n\n"
    report += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
    report += f"**Scan duration:** {elapsed_total:.2f} seconds\n"
    report += f"**Parallel compliance:** {'✅' if use_parallel_compliance else '❌'}\n"
    report += f"**Parallel stale branches:** {'✅' if use_parallel_stale else '❌'}\n\n"
    
    # 1. Compliance Audit
    compliance_results = results.get("compliance scan", {})
    if compliance_results:
        report += "## 1. Compliance Audit\n"
        report += "Checking for presence of `README.md`, `LICENSE`, `CODE_OF_CONDUCT.md`, and `CONTRIBUTING.md`.\n\n"
        report += "| Repository | README | LICENSE | CODE_OF_CONDUCT | CONTRIBUTING |\n"
        report += "|------------|--------|---------|-----------------|--------------|\n"
        
        for repo, status in compliance_results.items():
            if isinstance(status, dict):
                readme = "✅" if status.get('README.md') else "❌"
                license_ok = "✅" if status.get('LICENSE') else "❌"
                coc = "✅" if status.get('CODE_OF_CONDUCT.md') else "❌"
                contributing = "✅" if status.get('CONTRIBUTING.md') else "❌"
                report += f"| {repo} | {readme} | {license_ok} | {coc} | {contributing} |\n"
    else:
        report += "## 1. Compliance Audit\n*Scan failed or timed out*\n\n"
    
    # 2. Stale Branches
    stale_results = results.get("stale branch scan", {})
    report += "\n## 2. Stale Branches (>30 days)\n"
    if stale_results:
        report += "| Repository | Branch | Last Commit | Age (days) |\n"
        report += "|------------|--------|-------------|------------|\n"
        for repo, branches in stale_results.items():
            if isinstance(branches, list):
                for branch in branches:
                    report += f"| {repo} | {branch.get('name', 'N/A')} | {branch.get('date', 'N/A')} | {branch.get('age', 'N/A')} |\n"
    else:
        report += "No stale branches found or scan failed.\n"
    
    # 3. GitHub Pages Status
    pages_results = results.get("Pages status scan", {})
    report += "\n## 3. GitHub Pages Status\n"
    if pages_results:
        report += "| Repository | Status |\n"
        report += "|------------|--------|\n"
        for repo, status in pages_results.items():
            if isinstance(status, str):
                report += f"| {repo} | {status} |\n"
        
        # Admin blocked summary
        admin_blocked = [
            repo for repo, status in pages_results.items()
            if isinstance(status, str) and status.startswith("🚫 Admin Blocked")
        ]
        if admin_blocked:
            report += f"\n**Admin Blocked Pages: {len(admin_blocked)} repositories**\n"
            report += "Email help@agentvillage.org to request Pages enablement for:\n"
            for repo in admin_blocked[:10]:  # Show first 10
                repo_link = f"[{repo}](https://github.com/{repo})"
                report += f"- {repo_link}\n"
            if len(admin_blocked) > 10:
                report += f"- ... and {len(admin_blocked) - 10} more\n"
    else:
        report += "*Scan failed or timed out*\n"
    
    # 4. Workflow Health
    workflow_results = results.get("workflow health scan", {})
    report += "\n## 4. Workflow Health\n"
    if workflow_results:
        failing_workflows = []
        for repo, workflows in workflow_results.items():
            if isinstance(workflows, list):
                for wf in workflows:
                    if isinstance(wf, dict) and wf.get("status_text") == "Failing":
                        failing_workflows.append((repo, wf.get("name", "Unknown")))
        
        if failing_workflows:
            report += f"**Failing Workflows: {len(failing_workflows)}**\n"
            report += "Investigate recent runs and restart with:\n"
            for repo, wf_name in failing_workflows[:5]:  # Show first 5
                repo_link = f"[{repo}](https://github.com/{repo})"
                command = f'gh run list --workflow "{wf_name}" --repo {repo}'
                report += f"- {repo_link}: `{command}`\n"
            if len(failing_workflows) > 5:
                report += f"- ... and {len(failing_workflows) - 5} more\n"
        else:
            report += "No failing workflows detected.\n"
    else:
        report += "*Scan failed or timed out*\n"
    
    # 5. Activity Metrics
    open_prs = results.get("open PRs scan", {})
    open_issues = results.get("open issues scan", {})
    non_default_branches = results.get("non-default branches scan", {})
    
    report += "\n## 5. Activity Metrics\n"
    if isinstance(open_prs, dict):
        report += f"- **Open PRs:** {len(open_prs)}\n"
    if isinstance(open_issues, dict):
        report += f"- **Open Issues:** {len(open_issues)}\n"
    if isinstance(non_default_branches, dict):
        report += f"- **Non-default branches:** {len(non_default_branches)}\n"
    
    # 6. Dependency Audit
    dependency_results = results.get("dependency audit", {})
    if dependency_results:
        report += "\n## 6. Dependency Audit\n"
        total_deps = 0
        outdated_count = 0
        for repo, deps in dependency_results.items():
            if isinstance(deps, dict):
                for pm, data in deps.items():
                    if isinstance(data, dict):
                        # Old format with 'outdated' key
                        outdated = data.get('outdated', [])
                        outdated_count += len(outdated)
                        # Also count total dependencies if present
                        deps_list = data.get('dependencies', [])
                        total_deps += len(deps_list)
                    elif isinstance(data, list):
                        # Current format: list of dependency strings
                        total_deps += len(data)
        report += f"**Total dependencies found:** {total_deps}\n"
        if outdated_count > 0:
            report += f"**Outdated packages:** {outdated_count}\n"
    
    # 7. Shadowbanned agents
    shadowban_results = results.get("shadowban check", {})
    if shadowban_results:
        report += "\n## 7. Shadowbanned Agents\n"
        shadowbanned = [
            agent for agent, data in shadowban_results.items()
            if isinstance(data, dict) and data.get("status") == 404
        ]
        if shadowbanned:
            report += "Use git CLI, avoid web UI for these agents:\n"
            for agent in shadowbanned:
                report += f"- `{agent}`\n"
        else:
            report += "No shadowbanned agents detected.\n"
    
    return report

if __name__ == "__main__":
    generate_markdown_report_fixed()
