import subprocess
from .repo_utils import get_all_repos

REQUIRED_FILES = ['README.md', 'LICENSE', 'CODE_OF_CONDUCT.md']

def check_file_exists_gh(repo, filename):
    try:
        cmd = f"gh api repos/{repo}/contents/{filename} --silent"
        subprocess.check_call(cmd, shell=True, stderr=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        return False

def scan_repos():
    repos = get_all_repos()
    print(f"Scanning {len(repos)} repositories...\n")
    
    report = {}
    print(f"{'REPOSITORY':<45} | {'README':<8} | {'LICENSE':<8} | {'COC':<8}")
    print("-" * 80)
    
    for repo in repos:
        repo_status = {}
        for file in REQUIRED_FILES:
            exists = check_file_exists_gh(repo, file)
            repo_status[file] = exists
        
        readme = "✅" if repo_status['README.md'] else "❌"
        license_ok = "✅" if repo_status['LICENSE'] else "❌"
        coc = "✅" if repo_status['CODE_OF_CONDUCT.md'] else "❌"
        print(f"{repo:<45} | {readme:<8} | {license_ok:<8} | {coc:<8}")
        
        report[repo] = repo_status
    return report

if __name__ == '__main__':
    print("\n--- REPO HEALTH REPORT (via gh API) ---")
    scan_repos()
