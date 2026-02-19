import requests
import time

agents = [
    "claude-3-7-sonnet",
    "claude-opus-4-5", 
    "claude-opus-4-6",
    "claude-sonnet-4-6",
    "claude-sonnet-45",
    "claudehaiku45",
    "deepseek-v32",
    "gemini-25-pro-collab",
    "gemini-3-pro-ai-village",
    "gpt-5-1",
    "gpt-5-2",
    "gpt-5-ai-village",
    "opus-4-5-claude-code"
]

print(f"{'AGENT USERNAME':<30} | {'STATUS':<10} | {'URL'}")
print("-" * 75)

for agent in agents:
    url = f"https://github.com/{agent}"
    try:
        # We want to check as an unauthenticated user, so we don't send any headers
        response = requests.get(url)
        status = response.status_code
        print(f"{agent:<30} | {status:<10} | {url}")
    except Exception as e:
        print(f"{agent:<30} | {'ERROR':<10} | {e}")
    
    # Be polite to the API
    time.sleep(1)
