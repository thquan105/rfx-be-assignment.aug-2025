from fastapi import APIRouter

router = APIRouter()

@router.get("/notifications/ping")
def notifications_ping():
    return {"ok": True, "scope": "notifications"}
