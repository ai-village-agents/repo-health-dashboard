"""Scanner module for open PRs and open issues across the organization."""
import subprocess
import json
try:
    from .repo_utils import get_all_repos, ORG
except ImportError:
    import os, sys
    if __package__ is None or __package__ == '':
        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        if repo_root not in sys.path:
            sys.path.insert(0, repo_root)
        from src.scanner.repo_utils import get_all_repos, ORG
    else:
        raise


def scan_open_prs():
    """Scan all repos for open pull requests."""
    prs = []
    try:
        cmd = f"gh search prs --state=open --owner={ORG} --json repository,title,number,author,createdAt,url --limit 100"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
        if result.returncode == 0 and result.stdout.strip():
            data = json.loads(result.stdout)
            for pr in data:
                prs.append({
                    'repo': pr['repository']['name'],
                    'number': pr['number'],
                    'title': pr['title'],
                    'author': pr['author']['login'],
                    'created': pr['createdAt'][:10],
                    'url': pr['url'],
                })
    except Exception as e:
        print(f"Error scanning PRs: {e}")
    return prs


def scan_open_issues():
    """Scan all repos for open issues (excluding PRs)."""
    issues = []
    repos = get_all_repos()
    for repo in repos:
        try:
            cmd = f"gh issue list -R {repo} --state open --json number,title,author,createdAt,url --limit 20"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
            if result.returncode == 0 and result.stdout.strip():
                data = json.loads(result.stdout)
                repo_name = repo.split('/')[-1]
                for issue in data:
                    issues.append({
                        'repo': repo_name,
                        'number': issue['number'],
                        'title': issue['title'],
                        'author': issue['author']['login'],
                        'created': issue['createdAt'][:10],
                        'url': issue['url'],
                    })
        except Exception as e:
            print(f"Error scanning issues for {repo}: {e}")
    return issues


def scan_non_default_branches():
    """Scan all repos for non-default branches (not just stale ones)."""
    branch_data = {}
    repos = get_all_repos()
    for repo in repos:
        try:
            cmd = f"gh api repos/{repo}/branches --paginate"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
            if result.returncode == 0 and result.stdout.strip():
                branches = json.loads(result.stdout)
                non_default = []
                for branch in branches:
                    name = branch['name']
                    if name in ['main', 'master']:
                        continue
                    non_default.append(name)
                if non_default:
                    branch_data[repo.split('/')[-1]] = non_default
        except Exception as e:
            print(f"Error scanning branches for {repo}: {e}")
    return branch_data


if __name__ == '__main__':
    print("\n--- OPEN PRs ---")
    prs = scan_open_prs()
    if not prs:
        print("No open PRs!")
    else:
        for pr in prs:
            print(f"  {pr['repo']}#{pr['number']} by {pr['author']}: {pr['title']}")

    print("\n--- OPEN ISSUES ---")
    issues = scan_open_issues()
    if not issues:
        print("No open issues!")
    else:
        for issue in issues:
            print(f"  {issue['repo']}#{issue['number']} by {issue['author']}: {issue['title']}")

    print("\n--- NON-DEFAULT BRANCHES ---")
    branches = scan_non_default_branches()
    if not branches:
        print("No non-default branches!")
    else:
        for repo, brs in branches.items():
            for br in brs:
                print(f"  {repo}: {br}")
