import requests

TARGET_REPOS = [
    'ai-village-agents/park-cleanups',
    'ai-village-agents/park-cleanup-site',
    'ai-village-agents/open-ics-validator',
    'ai-village-agents/community-cleanup-toolkit',
    'ai-village-agents/community-action-framework',
    'ai-village-agents/repo-health-dashboard'
]

REQUIRED_FILES = ['README.md', 'LICENSE', 'CODE_OF_CONDUCT.md']
BRANCHES = ['main', 'master']

def check_file_exists(repo, filename):
    # Try different branches
    for branch in BRANCHES:
        # Try exact match
        url = f'https://raw.githubusercontent.com/{repo}/{branch}/{filename}'
        if requests.head(url).status_code == 200:
            return True
        
        # Try lowercase
        url_lower = f'https://raw.githubusercontent.com/{repo}/{branch}/{filename.lower()}'
        if requests.head(url_lower).status_code == 200:
            return True
            
    return False

def scan_repos():
    report = {}
    for repo in TARGET_REPOS:
        print(f"Scanning {repo}...")
        repo_status = {}
        for file in REQUIRED_FILES:
            repo_status[file] = check_file_exists(repo, file)
        report[repo] = repo_status
    return report

if __name__ == '__main__':
    results = scan_repos()
    
    print("\n--- REPO HEALTH REPORT ---")
    print(f"{'REPOSITORY':<45} | {'README':<8} | {'LICENSE':<8} | {'COC':<8}")
    print("-" * 80)
    
    for repo, status in results.items():
        readme = "✅" if status['README.md'] else "❌"
        license = "✅" if status['LICENSE'] else "❌"
        coc = "✅" if status['CODE_OF_CONDUCT.md'] else "❌"
        print(f"{repo:<45} | {readme:<8} | {license:<8} | {coc:<8}")
