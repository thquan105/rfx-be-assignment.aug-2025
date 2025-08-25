from fastapi import APIRouter

router = APIRouter()

@router.get("/reports/ping")
def reports_ping():
    return {"ok": True, "scope": "reports"}
