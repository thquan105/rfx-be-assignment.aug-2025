from fastapi import APIRouter

router = APIRouter()

@router.get("/attachments/ping")
def attachments_ping():
    return {"ok": True, "scope": "attachments"}
