import subprocess
import json
from datetime import datetime, timedelta, timezone
from repo_utils import get_all_repos

STALE_DAYS = 30

def get_branches(repo):
    try:
        cmd = f"gh api repos/{repo}/branches --paginate"
        output = subprocess.check_output(cmd, shell=True, stderr=subprocess.DEVNULL)
        return json.loads(output)
    except subprocess.CalledProcessError:
        return []

def get_commit_date(repo, sha):
    try:
        cmd = f"gh api repos/{repo}/commits/{sha}"
        output = subprocess.check_output(cmd, shell=True, stderr=subprocess.DEVNULL)
        data = json.loads(output)
        date_str = data['commit']['committer']['date']
        if date_str.endswith('Z'):
            date_str = date_str[:-1] + '+00:00'
        return datetime.fromisoformat(date_str)
    except (subprocess.CalledProcessError, KeyError, ValueError):
        return datetime.now(timezone.utc)

def scan_stale_branches():
    now = datetime.now(timezone.utc)
    stale_data = {}
    repos = get_all_repos()
    print(f"Scanning {len(repos)} repositories for stale branches...\n")

    for repo in repos:
        branches = get_branches(repo)
        repo_stale_branches = []
        
        for branch in branches:
            name = branch['name']
            if name in ['main', 'master']:
                continue
                
            sha = branch['commit']['sha']
            commit_date = get_commit_date(repo, sha)
            age = (now - commit_date).days
            
            if age > STALE_DAYS:
                repo_stale_branches.append({
                    'name': name,
                    'date': commit_date.strftime('%Y-%m-%d'),
                    'age': age
                })
        
        if repo_stale_branches:
            stale_data[repo] = repo_stale_branches

    return stale_data

if __name__ == '__main__':
    print(f"\n--- STALE BRANCH REPORT (Older than {STALE_DAYS} days) ---")
    results = scan_stale_branches()
    if not results:
        print("No stale branches found! Clean ecosystem.")
    else:
        for repo, branches in results.items():
            for branch in branches:
                print(f"{repo:<45} | {branch['name']:<30} | {branch['date']:<12} | {branch['age']:<8}")
