import requests
import os

ARKHAM = os.getenv("ARKHAM_KEY")

def arkham_profile(address):
    url = f"https://api.arkhamintelligence.com/wallet/{address}"
    headers = {"API-Key": ARKHAM}
    try:
        r = requests.get(url, headers=headers, timeout=5).json()
        return r
    except:
        return {}
