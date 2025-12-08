import requests
import os

ETHERSCAN = os.getenv("ETHERSCAN_KEY")

def get_wallet_tags(address):
    url = f"https://api.etherscan.io/api?module=account&action=balances&address={address}&apikey={ETHERSCAN}"
    try:
        r = requests.get(url, timeout=5).json()
        return r
    except:
        return {}
