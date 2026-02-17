import subprocess
import json
import sys

def get_pages_status(repo):
    """Check GitHub Pages status for a repository."""
    try:
        cmd = f"gh api repos/{repo}/pages --silent"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            data = json.loads(result.stdout)
            return {
                'enabled': True,
                'status': data.get('status', 'unknown'),
                'html_url': data.get('html_url', ''),
                'source': data.get('source', {})
            }
        else:
            # If 404, Pages not enabled
            if 'HTTP 404' in result.stderr:
                return {'enabled': False, 'error': 'Pages not enabled'}
            else:
                return {'enabled': False, 'error': result.stderr[:100]}
    except Exception as e:
        return {'enabled': False, 'error': str(e)}

def check_live_site(repo):
    """Check if the GitHub Pages site is live (HTTP 200)."""
    url = f"https://ai-village-agents.github.io/{repo.split('/')[1]}/"
    try:
        cmd = f"curl -s -o /dev/null -w '%{{http_code}}' {url}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            status_code = result.stdout.strip()
            return {'live': status_code == '200', 'status_code': status_code, 'url': url}
    except Exception as e:
        pass
    return {'live': False, 'status_code': 'unknown', 'url': url}

# Test with a few repos
test_repos = [
    'ai-village-agents/deepseek-news',
    'ai-village-agents/community-action-framework',
    'ai-village-agents/civic-safety-guardrails'
]

for repo in test_repos:
    print(f"\n=== {repo} ===")
    pages_status = get_pages_status(repo)
    print(f"Pages status: {pages_status}")
    if pages_status.get('enabled'):
        live_status = check_live_site(repo)
        print(f"Live check: {live_status}")
