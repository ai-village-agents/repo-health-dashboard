import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.scanner.compliance_check import scan_repos
from src.scanner.stale_branch_check import scan_stale_branches
from src.scanner.dependency_audit import audit_dependencies
from src.scanner.pages_check import scan_pages_status
from src.scanner.workflow_check import scan_workflow_health
from datetime import datetime

def generate_markdown_report():
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
    
    report = f"# AI Village Repository Health Report\n\n"
    report += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n"
    
    report += "## 1. Compliance Audit\n"
    report += "Checking for presence of `README.md`, `LICENSE`, `CODE_OF_CONDUCT.md`, and `CONTRIBUTING.md`.\n\n"
    report += "| Repository | README | LICENSE | CODE_OF_CONDUCT | CONTRIBUTING |\n"
    report += "|------------|--------|---------|-----------------|--------------|\n"
    
    for repo, status in compliance_results.items():
        readme = "✅" if status['README.md'] else "❌"
        license = "✅" if status['LICENSE'] else "❌"
        coc = "✅" if status['CODE_OF_CONDUCT.md'] else "❌"
        contributing = "✅" if status.get('CONTRIBUTING.md') else "❌"
        repo_link = f"[{repo}](https://github.com/{repo})"
        report += f"| {repo_link} | {readme} | {license} | {coc} | {contributing} |\n"
        
    total_repos = len(compliance_results)
    fully_compliant = sum(
        1 for status in compliance_results.values()
        if status.get('README.md') and status.get('LICENSE') and status.get('CODE_OF_CONDUCT.md') and status.get('CONTRIBUTING.md')
    )
    missing_any = total_repos - fully_compliant
    report += "\n### Summary\n"
    report += f"Scanned {total_repos} repositories. {fully_compliant} are fully compliant with all four required files, and {missing_any} are missing one or more files.\n"

    report += "\n## 2. Deployment Status (GitHub Pages)\n"
    report += "Tracks which repositories have active Pages sites vs. those blocked by admin permissions.\n\n"
    report += "| Repository | Status |\n"
    report += "|------------|--------|\n"

    for repo, status in pages_results.items():
        repo_link = f"[{repo}](https://github.com/{repo})"
        report += f"| {repo_link} | {status} |\n"

    report += "\n## 3. Workflow Health\n"
    report += "GitHub Actions workflow status across all repositories.\n\n"
    report += "| Repository | Workflow | Status | Last Run |\n"
    report += "|------------|----------|--------|----------|\n"

    wf_total = 0
    wf_passing = 0
    wf_failing = 0
    wf_disabled = 0
    wf_no_runs = 0
    wf_other = 0

    for repo, workflows in workflow_results.items():
        if not workflows:
            continue
        for wf in workflows:
            wf_total += 1
            st = wf["status_text"]
            if st == "Passing": wf_passing += 1
            elif st == "Failing": wf_failing += 1
            elif st == "Disabled": wf_disabled += 1
            elif st == "No runs": wf_no_runs += 1
            else: wf_other += 1

            repo_link = f"[{repo}](https://github.com/{repo})"
            status_str = f"{wf['status_icon']} {wf['status_text']}"
            report += f"| {repo_link} | {wf['name']} | {status_str} | {wf['last_run_date']} |\n"

    report += "\n### Summary\n"
    report += f"**{wf_total} workflows** across all repositories: "
    report += f"✅ {wf_passing} passing, ❌ {wf_failing} failing, 🚫 {wf_disabled} disabled, ⚪ {wf_no_runs} no runs"
    if wf_other:
        report += f", ⚠️ {wf_other} other"
    report += "\n"

    report += "\n## 4. Stale Branch Detector\n"
    report += "Branches older than 30 days (excluding main/master).\n\n"
    
    if not stale_results:
        report += "✅ **No stale branches found!** The ecosystem is clean.\n"
    else:
        report += "| Repository | Branch | Last Commit | Days Ago |\n"
        report += "|------------|--------|-------------|----------|\n"
        for repo, branches in stale_results.items():
            for branch in branches:
                report += f"| {repo} | {branch['name']} | {branch['date']} | {branch['age']} |\n"

    report += "\n## 5. Dependency Audit\n"
    report += "External libraries and tools used across the village.\n\n"
    
    for repo, deps in dependency_results.items():
        if not deps['python'] and not deps['javascript']:
            continue
            
        report += f"### [{repo}](https://github.com/{repo})\n"
        
        if deps['python']:
            report += "**Python:**\n"
            for d in deps['python']:
                report += f"- `{d}`\n"
        
        if deps['javascript']:
            report += "**JavaScript:**\n"
            for d in deps['javascript']:
                report += f"- `{d}`\n"
        report += "\n"

    with open("HEALTH_REPORT.md", "w") as f:
        f.write(report)
        
    print("\nReport generated: HEALTH_REPORT.md")

if __name__ == "__main__":
    generate_markdown_report()
