from fastapi import APIRouter

router = APIRouter()

@router.get("/projects/ping")
def projects_ping():
    return {"ok": True, "scope": "projects"}
