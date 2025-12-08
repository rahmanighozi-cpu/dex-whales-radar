import requests

DEX_API = "https://api.dexscreener.com/latest/dex/trades"

def fetch_latest_trades():
    try:
        r = requests.get(DEX_API, timeout=5).json()
        return r.get("data", [])
    except:
        return []
