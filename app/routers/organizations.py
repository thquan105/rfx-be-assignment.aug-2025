from fastapi import APIRouter

router = APIRouter()


@router.get("/organizations/ping")
def orgs_ping():
    return {"ok": True, "scope": "organizations"}
