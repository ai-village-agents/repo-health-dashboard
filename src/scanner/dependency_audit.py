import subprocess
import json
import base64

TARGET_REPOS = [
    'ai-village-agents/park-cleanups',
    'ai-village-agents/park-cleanup-site',
    'ai-village-agents/community-cleanup-toolkit',
    'ai-village-agents/community-action-framework',
    'ai-village-agents/repo-health-dashboard',
    'ai-village-agents/which-ai-village-agent',
    'ai-village-agents/civic-safety-guardrails',
]

def get_file_content(repo, filename):
    try:
        cmd = f"gh api repos/{repo}/contents/{filename}"
        output = subprocess.check_output(cmd, shell=True, stderr=subprocess.DEVNULL)
        data = json.loads(output)
        content = base64.b64decode(data['content']).decode('utf-8')
        return content
    except subprocess.CalledProcessError:
        return None

def parse_requirements(content):
    dependencies = []
    for line in content.splitlines():
        line = line.strip()
        if line and not line.startswith('#'):
            dependencies.append(line)
    return dependencies

def parse_package_json(content):
    try:
        data = json.loads(content)
        deps = []
        if 'dependencies' in data:
            for k, v in data['dependencies'].items():
                deps.append(f"{k}: {v}")
        if 'devDependencies' in data:
            for k, v in data['devDependencies'].items():
                deps.append(f"{k}: {v} (dev)")
        return deps
    except json.JSONDecodeError:
        return []

def audit_dependencies():
    audit_data = {}
    
    for repo in TARGET_REPOS:
        repo_deps = {'python': [], 'javascript': []}
        
        # Check Python
        req_content = get_file_content(repo, 'requirements.txt')
        if req_content:
            repo_deps['python'] = parse_requirements(req_content)
            
        # Check JavaScript
        pkg_content = get_file_content(repo, 'package.json')
        if pkg_content:
            repo_deps['javascript'] = parse_package_json(pkg_content)
            
        if repo_deps['python'] or repo_deps['javascript']:
            audit_data[repo] = repo_deps
            
    return audit_data

if __name__ == '__main__':
    print("\n--- DEPENDENCY AUDIT ---")
    results = audit_dependencies()
    for repo, deps in results.items():
        if not deps['python'] and not deps['javascript']:
            continue
            
        print(f"\n{repo}:")
        if deps['python']:
            print("  Python:")
            for d in deps['python']:
                print(f"    - {d}")
        if deps['javascript']:
            print("  JavaScript:")
            for d in deps['javascript']:
                print(f"    - {d}")
