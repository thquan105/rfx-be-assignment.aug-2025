from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User, UserRole
from app.utils.security import hash_password


class UserRepository:
    """Data access layer for users."""

    @staticmethod
    def get_by_id(db: Session, user_id: int) -> User | None:
        return db.get(User, user_id)

    @staticmethod
    def get_by_email(db: Session, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        return db.execute(stmt).scalar_one_or_none()

    @staticmethod
    def list_by_org(db: Session, org_id: int) -> list[User]:
        stmt = select(User).where(User.org_id == org_id)
        return list(db.execute(stmt).scalars().all())

    @staticmethod
    def create_in_org(
        db: Session,
        *,
        org_id: int,
        email: str,
        password: str,
        full_name: str | None,
        role: str
    ) -> User:
        user = User(
            org_id=org_id,
            email=email,
            password_hash=hash_password(password),
            full_name=full_name,
            role=UserRole(role),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
