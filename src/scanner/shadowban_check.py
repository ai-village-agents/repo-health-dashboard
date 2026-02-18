import requests
import time

def check_shadowbans():
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
    
    results = {}
    
    print("Scanning agent profiles for visibility (shadowban check)...")
    
    for agent in agents:
        url = f"https://github.com/{agent}"
        try:
            # We want to check as an unauthenticated user
            response = requests.get(url)
            status = response.status_code
            results[agent] = {
                "status": status,
                "url": url
            }
        except Exception as e:
             results[agent] = {
                "status": "ERROR",
                "url": url,
                "error": str(e)
            }
        # Be polite to the API
        time.sleep(0.5)
        
    return results
