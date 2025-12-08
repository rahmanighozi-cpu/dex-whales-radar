from fastapi import APIRouter
from services.dexscreener import fetch_latest_trades
from database.redis import r

router = APIRouter()

THRESHOLD = 10000  # USD

@router.get("/live")
def whale_live():
    trades = fetch_latest_trades()
    whales = []

    for t in trades:
        if t["usdValue"] >= THRESHOLD:
            whales.append({
                "token": t["baseToken"]["symbol"],
                "chain": t["chainId"],
                "amount": t["usdValue"],
                "tx": t["transactionHash"],
            })

    return whales
