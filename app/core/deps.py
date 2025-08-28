from typing import Callable
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from app.config import settings
from app.database import get_db
from app.repositories.user_repository import UserRepository
from app.schemas.auth import TokenPayload

# Token URL for Swagger login (not used as form, but required by OAuth2PasswordBearer)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    """Decode JWT, fetch the current user from DB, and return it."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        data = TokenPayload(**payload)
    except (JWTError, ValueError):
        raise credentials_exception

    user = UserRepository.get_by_id(db, int(data.sub))
    if not user or user.org_id != data.org_id:
        raise credentials_exception
    return user


def require_roles(*roles: str) -> Callable:
    """Dependency factory to enforce role-based access on endpoints."""
    def checker(current_user = Depends(get_current_user)):
        if current_user.role.value not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return current_user
    return checker
