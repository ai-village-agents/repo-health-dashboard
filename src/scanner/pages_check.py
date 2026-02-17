import subprocess
import json
from .repo_utils import get_all_repos

def check_pages_status(repo):
    """
    Checks the GitHub Pages status for a repository.
    Returns:
    - '✅ Live': If Pages is enabled and built.
    - '🚫 Admin Blocked': If Pages is not found (404), likely needing admin enablement.
    - '⚠️ Error': If another error occurs.
    """
    try:
        # Check if Pages is enabled
        cmd = f"gh api repos/{repo}/pages"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            data = json.loads(result.stdout)
            return f"✅ Live ({data.get('html_url', '')})"
        elif "Not Found" in result.stderr or "404" in result.stderr:
            return "🚫 Admin Blocked"
        else:
            return f"⚠️ Error: {result.stderr.strip()}"
            
    except Exception as e:
        return f"⚠️ Exception: {str(e)}"

def scan_pages_status():
    repos = get_all_repos()
    print(f"Scanning Pages status for {len(repos)} repositories...\n")
    
    report = {}
    for repo in repos:
        status = check_pages_status(repo)
        report[repo] = status
        print(f"{repo:<45} | {status}")
        
    return report
