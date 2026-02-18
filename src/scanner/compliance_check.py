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

REMEDIATION_STEPS = {
    'README.md': (
        "gh repo clone {repo} && cd {repo_dir} && "
        "printf '# {repo_dir}\\n\\nProject overview.' > README.md && "
        "git add README.md && git commit -m \"Add README\" && git push"
    ),
    'LICENSE': (
        "gh repo clone {repo} && cd {repo_dir} && "
        "curl -o LICENSE https://raw.githubusercontent.com/github/choosealicense.com/gh-pages/_licenses/mit.txt && "
        "git add LICENSE && git commit -m \"Add MIT license\" && git push"
    ),
    'CODE_OF_CONDUCT.md': (
        "gh repo clone {repo} && cd {repo_dir} && "
        "curl -o CODE_OF_CONDUCT.md https://raw.githubusercontent.com/github/docs/main/content/site-policy/code-of-conduct.md && "
        "git add CODE_OF_CONDUCT.md && git commit -m \"Add code of conduct\" && git push"
    ),
    'CONTRIBUTING.md': (
        "gh repo clone {repo} && cd {repo_dir} && "
        "printf '## Contributing\\n\\nPull requests welcome.\\n' > CONTRIBUTING.md && "
        "git add CONTRIBUTING.md && git commit -m \"Add contributing guide\" && git push"
    ),
}

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
    failures = {}
    print(f"{'REPOSITORY':<45} | {'README':<8} | {'LICENSE':<8} | {'COC':<8} | {'CONTRIBUTING':<12}")
    print("-" * 98)
    
    for repo in repos:
        repo_status = {}
        for file in REQUIRED_FILES:
            exists = check_file_exists_gh(repo, file)
            repo_status[file] = exists
        
        missing_files = [fname for fname, present in repo_status.items() if not present]
        if missing_files:
            failures[repo] = missing_files
        
        readme = "✅" if repo_status['README.md'] else "❌"
        license_ok = "✅" if repo_status['LICENSE'] else "❌"
        coc = "✅" if repo_status['CODE_OF_CONDUCT.md'] else "❌"
        contributing = "✅" if repo_status['CONTRIBUTING.md'] else "❌"
        print(f"{repo:<45} | {readme:<8} | {license_ok:<8} | {coc:<8} | {contributing:<12}")
        
        report[repo] = repo_status

    print("\nRemediation Plan:")
    if not failures:
        print("All required files are present across all repositories.")
    else:
        for repo, missing in failures.items():
            repo_dir = repo.split('/')[-1]
            print(f"- {repo}:")
            for fname in missing:
                instruction = REMEDIATION_STEPS.get(fname)
                if instruction:
                    instruction_text = instruction.format(repo=repo, repo_dir=repo_dir)
                else:
                    instruction_text = f"Add {fname} to the repository and push the change."
                print(f"  - {fname}: {instruction_text}")
    return report

if __name__ == '__main__':
    print("\n--- REPO HEALTH REPORT (via gh API) ---")
    scan_repos()
