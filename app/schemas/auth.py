from pydantic import BaseModel, EmailStr

from app.schemas.org import OrgOut
from app.schemas.user import UserOut


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str
    org_id: int
    role: str


class RegisterRequest(BaseModel):
    org_name: str
    email: EmailStr
    password: str
    full_name: str | None = None


class RegisterResponse(BaseModel):
    organization: OrgOut
    admin: UserOut
    token: Token
