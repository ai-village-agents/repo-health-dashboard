import subprocess
import json
import sys
import os

try:
    from .repo_utils import get_all_repos
except ImportError:
    if __package__ is None or __package__ == '':
        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        if repo_root not in sys.path:
            sys.path.insert(0, repo_root)
        from src.scanner.repo_utils import get_all_repos
    else:
        raise

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

if __name__ == "__main__":
    scan_pages_status()
