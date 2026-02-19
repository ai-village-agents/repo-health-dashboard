import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.scanner.compliance_check import scan_repos
from src.scanner.stale_branch_check import scan_stale_branches
from src.scanner.dependency_audit import audit_dependencies
from src.scanner.pages_status_check import scan_pages_status
from datetime import datetime

def generate_markdown_report():
    print("Running compliance scan...")
    compliance_results = scan_repos()
    
    print("Running stale branch scan...")
    stale_results = scan_stale_branches()

    print("Running dependency audit...")
    dependency_results = audit_dependencies()
    
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
        contributing = "✅" if status['CONTRIBUTING.md'] else "❌"
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

    report += "\n## 3. Dependency Audit\n"
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

    print("Running GitHub Pages status scan...")
    pages_results = scan_pages_status()

    report += "\n## 4. GitHub Pages Status\n"
    report += "GitHub Pages enablement across organization repositories.\n\n"
    report += "| Repository | Pages | Status | URL |\n"
    report += "|------------|-------|--------|-----|\n"

    enabled = not_enabled = forbidden = errors = 0
    for repo, info in pages_results.items():
        pages = "✅" if info.get('enabled') else "❌"
        status = info.get('status') or 'error'
        url = info.get('pages_url') or ''
        if status == 'enabled':
            enabled += 1
        elif status == 'not_enabled':
            not_enabled += 1
        elif status == 'forbidden':
            forbidden += 1
        else:
            errors += 1

        repo_link = f"[{repo}](https://github.com/{repo})"
        report += f"| {repo_link} | {pages} | {status} | {url} |\n"

    report += "\n"
    report += (
        f"Scanned {len(pages_results)} repos. Enabled: {enabled}. Not enabled: {not_enabled}. "
        f"Forbidden: {forbidden}. Errors: {errors}.\n"
    )

    with open("HEALTH_REPORT.md", "w") as f:
        f.write(report)
        
    print("\nReport generated: HEALTH_REPORT.md")

if __name__ == "__main__":
    generate_markdown_report()
