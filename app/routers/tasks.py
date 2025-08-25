from fastapi import APIRouter

router = APIRouter()

@router.get("/tasks/ping")
def tasks_ping():
    return {"ok": True, "scope": "tasks"}
