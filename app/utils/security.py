from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from jose import jwt
from passlib.context import CryptContext

from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = settings.algorithm
SECRET_KEY = settings.secret_key
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes


def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a bcrypt hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    *, sub: str, org_id: int, role: str, expires_delta: Optional[timedelta] = None
) -> str:
    """Create a signed JWT access token with standard claims.

    sub: subject (user id as string)
    org_id: user's organization id
    role: user's role string (admin/manager/member)
    expires_delta: custom expiry duration; default from settings
    """
    now = datetime.now(timezone.utc)
    expire = now + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode: dict[str, Any] = {
        "sub": sub,
        "org_id": org_id,
        "role": role,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
