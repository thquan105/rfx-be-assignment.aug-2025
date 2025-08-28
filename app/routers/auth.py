from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.auth import LoginRequest, Token, RegisterRequest, RegisterResponse
from app.services.auth_service import AuthService
from app.schemas.org import OrgOut
from app.schemas.user import UserOut

router = APIRouter()

@router.post("/auth/login", response_model=Token)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    token = AuthService.authenticate(db, email=payload.email, password=payload.password)
    return {"access_token": token, "token_type": "bearer"}


@router.post("/auth/register", response_model=RegisterResponse, summary="Register and create organization")
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    org, user, token = AuthService.register_and_create_org(
        db,
        org_name=payload.org_name,
        email=payload.email,
        password=payload.password,
        full_name=payload.full_name
    )
    return {
        "organization": OrgOut.model_validate(org),
        "admin": UserOut.model_validate(user),
        "token": {"access_token": token, "token_type": "bearer"}
    }
