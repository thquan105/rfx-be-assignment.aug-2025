from fastapi import APIRouter

router = APIRouter()

@router.get("/comments/ping")
def comments_ping():
    return {"ok": True, "scope": "comments"}
