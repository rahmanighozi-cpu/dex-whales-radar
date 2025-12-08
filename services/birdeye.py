import requests

BIRD_API = "https://public-api.birdeye.so/public/markets/trending"

def fetch_trending_sol():
    try:
        r = requests.get(BIRD_API, timeout=5).json()
        return r.get("data", [])
    except:
        return []
