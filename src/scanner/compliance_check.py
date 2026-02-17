import subprocess

try:
    from .repo_utils import get_all_repos
except ImportError:
    # Fallback for direct script execution
    from repo_utils import get_all_repos

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
    print(f"{'REPOSITORY':<45} | {'README':<8} | {'LICENSE':<8} | {'COC':<8}")
    print("-" * 80)
    
    for repo in repos:
        readme = "✅" if check_file_exists_gh(repo, "README.md") else "❌"
        license_file = "✅" if check_file_exists_gh(repo, "LICENSE") else "❌"
        coc = "✅" if check_file_exists_gh(repo, "CODE_OF_CONDUCT.md") else "❌"
        print(f"{repo:<45} | {readme:<8} | {license_file:<8} | {coc:<8}")

if __name__ == "__main__":
    scan_repos()
