from fastapi import FastAPI
from routers.whales import router as whale_router
from routers.memecoins import router as memecoin_router
from routers.smartmoney import router as smart_router
from routers.alerts import router as alert_router
from services.scheduler import start_scheduler

app = FastAPI(
    title="Frontier Tracker — Next Gen Chain Intelligence",
    version="1.0.0",
)

# register routes
app.include_router(whale_router, prefix="/whales")
app.include_router(memecoin_router, prefix="/memecoins")
app.include_router(smart_router, prefix="/smartmoney")
app.include_router(alert_router, prefix="/alerts")

@app.on_event("startup")
async def startup_event():
    start_scheduler()

@app.get("/")
async def root():
    return {"status": "Frontier Tracker is running"}
