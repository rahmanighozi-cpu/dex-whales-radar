import requests

def fetch_sol_holder_addresses(token):
    url = f"https://api.solscan.io/token/holders?tokenAddress={token}"
    try:
        r = requests.get(url, timeout=5).json()
        return r.get("data", [])
    except:
        return []
