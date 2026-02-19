"""
GitHub Pages status scanner.
Checks if a repository has a live GitHub Pages site.
"""
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
    Check if a repository has a live GitHub Pages site.
    
    Args:
        repo: Full repository name (e.g., 'ai-village-agents/deepseek-news')
        
    Returns:
        dict with keys:
        - live: bool (HTTP 200)
        - status_code: str HTTP status code
        - url: str full GitHub Pages URL
        - enabled: bool (True if status_code == 200, else False)
    """
    # Extract repo name from full path
    repo_name = repo.split('/')[1]
    url = f"https://ai-village-agents.github.io/{repo_name}/"
    
    try:
        # Use curl to check HTTP status
        cmd = f"curl -s -o /dev/null -w '%{{http_code}}' --max-time 10 {url}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            status_code = result.stdout.strip()
            live = status_code == '200'
            return {
                'live': live,
                'status_code': status_code,
                'url': url,
                'enabled': live  # Simplified: if live, we assume Pages enabled
            }
        else:
            # curl failed (timeout, network error, etc.)
            return {
                'live': False,
                'status_code': 'error',
                'url': url,
                'enabled': False,
                'error': result.stderr[:100] if result.stderr else 'curl failed'
            }
    except Exception as e:
        return {
            'live': False,
            'status_code': 'exception',
            'url': url,
            'enabled': False,
            'error': str(e)[:100]
        }

def scan_pages():
    """
    Scan all repositories for GitHub Pages status.
    
    Returns:
        dict mapping repository name to pages status dict
    """
    repos = get_all_repos()
    print(f"Scanning {len(repos)} repositories for GitHub Pages status...")
    
    results = {}
    for repo in repos:
        status = check_pages_status(repo)
        results[repo] = status
    
    return results

if __name__ == "__main__":
    # Test the scanner
    results = scan_pages()
    
    print("\nGitHub Pages Status Report:")
    print("-" * 80)
    for repo, status in results.items():
        indicator = "✅" if status['live'] else "❌"
        print(f"{repo:50} {indicator} HTTP {status['status_code']} ({status['url']})")
    
    live_count = sum(1 for status in results.values() if status['live'])
    total = len(results)
    print(f"\nSummary: {live_count}/{total} repositories have live GitHub Pages sites.")
