from fastapi import APIRouter

router = APIRouter()

@router.get("/users/ping")
def users_ping():
    return {"ok": True, "scope": "users"}
