"""Shared utilities for repo health scanning."""
import subprocess
import json

ORG = "ai-village-agents"

def get_all_repos():
    """Dynamically fetch all repos from the organization."""
    try:
        cmd = f"gh api /orgs/{ORG}/repos?per_page=100 --paginate"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        repos = json.loads(result.stdout)
        # Filter out archived repos and return full names
        return sorted([f"{ORG}/{r['name']}" for r in repos if not r.get('archived', False)])
    except Exception as e:
        print(f"Error fetching repos: {e}")
        # Fallback to known repos
        return [
            'ai-village-agents/park-cleanups',
            'ai-village-agents/park-cleanup-site',
            'ai-village-agents/community-cleanup-toolkit',
            'ai-village-agents/community-action-framework',
            'ai-village-agents/repo-health-dashboard',
            'ai-village-agents/which-ai-village-agent',
            'ai-village-agents/civic-safety-guardrails',
            'ai-village-agents/open-ics',
            'ai-village-agents/village-time-capsule',
        ]
