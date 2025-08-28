from typing import List
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.user import UserOut, UserCreate, PasswordUpdate
from app.core.deps import get_current_user, require_roles
from app.repositories.user_repository import UserRepository
from app.utils.security import verify_password, hash_password

router = APIRouter()

@router.get("/users/me", response_model=UserOut, summary="Get current user profile")
def get_me(current_user = Depends(get_current_user)):
    return current_user


@router.get("/users", response_model=List[UserOut], summary="List users in my organization")
def list_users(db: Session = Depends(get_db), current_user = Depends(require_roles("admin", "manager"))):
    return UserRepository.list_by_org(db, current_user.org_id)


@router.post("/users", response_model=UserOut, summary="Admin: create a user in my organization")
def create_user(payload: UserCreate, db: Session = Depends(get_db), current_user = Depends(require_roles("admin"))):
    # Admin creates users in their own organization; org_id comes from token/current user
    user = UserRepository.create_in_org(
        db,
        org_id=current_user.org_id,
        email=payload.email,
        password=payload.password,
        full_name=payload.full_name,
        role=payload.role,
    )
    return user


@router.patch("/users/me/password", summary="Change my password")
def change_password(payload: PasswordUpdate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    if not verify_password(payload.current_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    current_user.password_hash = hash_password(payload.new_password)
    db.add(current_user)
    db.commit()
    return {"msg": "Password updated successfully"}
