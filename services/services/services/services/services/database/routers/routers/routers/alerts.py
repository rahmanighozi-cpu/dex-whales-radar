from fastapi import APIRouter
from database.redis import r

router = APIRouter()

@router.get("/all")
def all_alerts():
    return r.lrange("alerts", 0, -1)
