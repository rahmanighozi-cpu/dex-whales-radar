from apscheduler.schedulers.background import BackgroundScheduler
from services.dexscreener import fetch_latest_trades
from database.redis import r

def scan_whales():
    trades = fetch_latest_trades()
    for t in trades:
        if t["usdValue"] >= 15000:
            r.lpush("alerts", f"BIG BUY: {t['baseToken']['symbol']} ${t['usdValue']}")

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(scan_whales, "interval", seconds=20)
    scheduler.start()
