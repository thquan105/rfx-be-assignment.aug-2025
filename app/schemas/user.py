from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None

    model_config = {"from_attributes": True}  # allow ORM object -> schema


class UserCreate(UserBase):
    password: str = Field(min_length=6)
    role: str = "member"


class UserOut(UserBase):
    id: int
    org_id: int
    role: str


class PasswordUpdate(BaseModel):
    current_password: str
    new_password: str = Field(min_length=6)
