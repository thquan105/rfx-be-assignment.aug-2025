from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.organization_repository import OrganizationRepository
from app.repositories.user_repository import UserRepository
from app.utils.security import create_access_token, verify_password


class AuthService:
    @staticmethod
    def authenticate(db: Session, *, email: str, password: str) -> str:
        user = UserRepository.get_by_email(db, email)
        if not user or not verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
            )
        token = create_access_token(
            sub=str(user.id), org_id=user.org_id, role=user.role.value
        )
        return token

    @staticmethod
    def register_and_create_org(
        db: Session, *, org_name: str, email: str, password: str, full_name: str | None
    ):
        if UserRepository.get_by_email(db, email):
            raise HTTPException(status_code=409, detail="Email already registered")
        org = OrganizationRepository.create(db, name=org_name)
        user = UserRepository.create_in_org(
            db,
            org_id=org.id,
            email=email,
            password=password,
            full_name=full_name,
            role="admin",
        )
        token = create_access_token(
            sub=str(user.id), org_id=user.org_id, role=user.role.value
        )
        return org, user, token
