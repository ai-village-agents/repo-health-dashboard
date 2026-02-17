import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.scanner.compliance_check import scan_repos
from src.scanner.stale_branch_check import scan_stale_branches
from src.scanner.dependency_audit import audit_dependencies
from src.scanner.pages_check import scan_pages_status
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
    
    report = f"# AI Village Repository Health Report\n\n"
    report += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n"
    
    report += "## 1. Compliance Audit\n"
    report += "Checking for presence of `README.md`, `LICENSE`, and `CODE_OF_CONDUCT.md`.\n\n"
    report += "| Repository | README | LICENSE | CODE_OF_CONDUCT |\n"
    report += "|------------|--------|---------|-----------------|\n"
    
    for repo, status in compliance_results.items():
        readme = "✅" if status['README.md'] else "❌"
        license = "✅" if status['LICENSE'] else "❌"
        coc = "✅" if status['CODE_OF_CONDUCT.md'] else "❌"
        repo_link = f"[{repo}](https://github.com/{repo})"
        report += f"| {repo_link} | {readme} | {license} | {coc} |\n"
        
    report += "\n## 2. Deployment Status (GitHub Pages)\n"
    report += "Tracks which repositories have active Pages sites vs. those blocked by admin permissions.\n\n"
    report += "| Repository | Status |\n"
    report += "|------------|--------|\n"

    for repo, status in pages_results.items():
        repo_link = f"[{repo}](https://github.com/{repo})"
        report += f"| {repo_link} | {status} |\n"

    report += "\n## 3. Stale Branch Detector\n"
    report += "Branches older than 30 days (excluding main/master).\n\n"
    
    if not stale_results:
        report += "✅ **No stale branches found!** The ecosystem is clean.\n"
    else:
        report += "| Repository | Branch | Last Commit | Days Ago |\n"
        report += "|------------|--------|-------------|----------|\n"
        for repo, branches in stale_results.items():
            for branch in branches:
                report += f"| {repo} | {branch['name']} | {branch['date']} | {branch['age']} |\n"

    report += "\n## 4. Dependency Audit\n"
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
