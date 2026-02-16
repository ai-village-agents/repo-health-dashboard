import sys
import os
# Add project root to path so we can import from src.scanner
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.scanner.compliance_check import scan_repos
from src.scanner.stale_branch_check import scan_stale_branches
from datetime import datetime

def generate_markdown_report():
    print("Running compliance scan...")
    compliance_results = scan_repos()
    
    print("Running stale branch scan...")
    stale_results = scan_stale_branches()
    
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
        # Link the repo name to the repo
        repo_link = f"[{repo}](https://github.com/{repo})"
        report += f"| {repo_link} | {readme} | {license} | {coc} |\n"
        
    report += "\n## 2. Stale Branch Detector\n"
    report += "Branches older than 30 days (excluding main/master).\n\n"
    
    if not stale_results:
        report += "✅ **No stale branches found!** The ecosystem is clean.\n"
    else:
        report += "| Repository | Branch | Last Commit | Days Ago |\n"
        report += "|------------|--------|-------------|----------|\n"
        for repo, branches in stale_results.items():
            for branch in branches:
                report += f"| {repo} | {branch['name']} | {branch['date']} | {branch['age']} |\n"
                
    with open("HEALTH_REPORT.md", "w") as f:
        f.write(report)
        
    print("\nReport generated: HEALTH_REPORT.md")

if __name__ == "__main__":
    generate_markdown_report()
