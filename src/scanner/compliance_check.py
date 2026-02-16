import subprocess
import json

TARGET_REPOS = [
    'ai-village-agents/park-cleanups',
    'ai-village-agents/park-cleanup-site',
    'ai-village-agents/community-cleanup-toolkit',
    'ai-village-agents/community-action-framework',
    'ai-village-agents/repo-health-dashboard',
    'ai-village-agents/which-ai-village-agent',
    'ai-village-agents/civic-safety-guardrails',
    'ai-village-agents/open-ics',
]

REQUIRED_FILES = ['README.md', 'LICENSE', 'CODE_OF_CONDUCT.md']

def check_file_exists_gh(repo, filename):
    try:
        # Use gh api to check contents
        # We look for the file in the root directory
        cmd = f"gh api repos/{repo}/contents/{filename} --silent"
        subprocess.check_call(cmd, shell=True, stderr=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        return False

def scan_repos():
    report = {}
    print(f"{'REPOSITORY':<45} | {'README':<8} | {'LICENSE':<8} | {'COC':<8}")
    print("-" * 80)
    
    for repo in TARGET_REPOS:
        repo_status = {}
        for file in REQUIRED_FILES:
            exists = check_file_exists_gh(repo, file)
            repo_status[file] = exists
        
        readme = "✅" if repo_status['README.md'] else "❌"
        license = "✅" if repo_status['LICENSE'] else "❌"
        coc = "✅" if repo_status['CODE_OF_CONDUCT.md'] else "❌"
        print(f"{repo:<45} | {readme:<8} | {license:<8} | {coc:<8}")
        
        report[repo] = repo_status
    return report

if __name__ == '__main__':
    print("\n--- REPO HEALTH REPORT (via gh API) ---")
    scan_repos()
