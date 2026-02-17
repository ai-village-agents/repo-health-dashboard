import os
import sys
import subprocess

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

REQUIRED_FILES = ['README.md', 'LICENSE', 'CODE_OF_CONDUCT.md', 'CONTRIBUTING.md']

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
    print(f"{'REPOSITORY':<45} | {'README':<8} | {'LICENSE':<8} | {'COC':<8} | {'CONTRIBUTING':<12}")
    print("-" * 98)
    
    for repo in repos:
        repo_status = {}
        for file in REQUIRED_FILES:
            exists = check_file_exists_gh(repo, file)
            repo_status[file] = exists
        
        readme = "✅" if repo_status['README.md'] else "❌"
        license_ok = "✅" if repo_status['LICENSE'] else "❌"
        coc = "✅" if repo_status['CODE_OF_CONDUCT.md'] else "❌"
        contributing = "✅" if repo_status['CONTRIBUTING.md'] else "❌"
        print(f"{repo:<45} | {readme:<8} | {license_ok:<8} | {coc:<8} | {contributing:<12}")
        
        report[repo] = repo_status
    return report

if __name__ == '__main__':
    print("\n--- REPO HEALTH REPORT (via gh API) ---")
    scan_repos()
