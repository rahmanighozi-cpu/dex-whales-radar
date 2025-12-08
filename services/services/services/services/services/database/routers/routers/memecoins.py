from fastapi import APIRouter
from services.birdeye import fetch_trending_sol
from services.dexscreener import fetch_latest_trades

router = APIRouter()

@router.get("/new")
def new_memecoins():
    sol_trending = fetch_trending_sol()
    evm_trades = fetch_latest_trades()

    meme_new = []

    for t in evm_trades:
        if t["usdValue"] < 50000 and t["liquidity"]["usd"] < 80000:
            meme_new.append({
                "symbol": t["baseToken"]["symbol"],
                "chain": t["chainId"],
                "tx": t["transactionHash"],
                "type": "New / Microcap"
            })

    return {
        "solana_trending": sol_trending[:20],
        "evm_new": meme_new[:20]
    }
