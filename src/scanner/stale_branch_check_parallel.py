"""
Parallel stale branch scanner using ThreadPoolExecutor.
"""
import os
import sys
import subprocess
import json
import concurrent.futures
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any

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

STALE_DAYS = 30

def get_branches(repo: str) -> List[Dict[str, Any]]:
    """Get all branches for a repository."""
    try:
        cmd = f"gh api repos/{repo}/branches --paginate"
        output = subprocess.check_output(cmd, shell=True, stderr=subprocess.DEVNULL, timeout=10)
        return json.loads(output)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, json.JSONDecodeError):
        return []

def get_commit_date(repo: str, sha: str) -> datetime:
    """Get commit date for a specific SHA."""
    try:
        cmd = f"gh api repos/{repo}/commits/{sha}"
        output = subprocess.check_output(cmd, shell=True, stderr=subprocess.DEVNULL, timeout=10)
        data = json.loads(output)
        date_str = data['commit']['committer']['date']
        if date_str.endswith('Z'):
            date_str = date_str[:-1] + '+00:00'
        return datetime.fromisoformat(date_str)
    except (subprocess.CalledProcessError, KeyError, ValueError, subprocess.TimeoutExpired, json.JSONDecodeError):
        return datetime.now(timezone.utc)

def process_repo_branches(repo: str) -> List[Dict[str, Any]]:
    """Process a single repository to find stale branches."""
    branches = get_branches(repo)
    if not branches:
        return []
    
    now = datetime.now(timezone.utc)
    stale_branches = []
    
    for branch in branches:
        name = branch['name']
        if name in ['main', 'master']:
            continue
            
        sha = branch['commit']['sha']
        commit_date = get_commit_date(repo, sha)
        age = (now - commit_date).days
        
        if age > STALE_DAYS:
            stale_branches.append({
                'name': name,
                'date': commit_date.strftime('%Y-%m-%d'),
                'age': age
            })
    
    return stale_branches

def scan_stale_branches_parallel(max_workers: int = 5) -> Dict[str, List[Dict[str, Any]]]:
    """Scan repositories for stale branches in parallel."""
    repos = get_all_repos()
    print(f"Scanning {len(repos)} repositories for stale branches in parallel (max_workers={max_workers})...")
    
    stale_data = {}
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_repo = {
            executor.submit(process_repo_branches, repo): repo
            for repo in repos
        }
        
        for future in concurrent.futures.as_completed(future_to_repo):
            repo = future_to_repo[future]
            try:
                stale_branches = future.result(timeout=30)
                if stale_branches:
                    stale_data[repo] = stale_branches
                    print(f"⚠️ {repo}: {len(stale_branches)} stale branches")
                else:
                    print(f"✅ {repo}: No stale branches")
            except concurrent.futures.TimeoutError:
                print(f"⏱️ {repo}: TIMEOUT")
            except Exception as e:
                print(f"❌ {repo}: ERROR - {e}")
    
    return stale_data

def scan_stale_branches() -> Dict[str, List[Dict[str, Any]]]:
    """Wrapper for backward compatibility."""
    return scan_stale_branches_parallel(max_workers=5)

if __name__ == '__main__':
    print(f"\n--- STALE BRANCH REPORT (Parallel, Older than {STALE_DAYS} days) ---")
    results = scan_stale_branches_parallel()
    if not results:
        print("No stale branches found! Clean ecosystem.")
    else:
        for repo, branches in results.items():
            for branch in branches:
                print(f"{repo:<45} | {branch['name']:<30} | {branch['date']:<12} | {branch['age']:<8}")
