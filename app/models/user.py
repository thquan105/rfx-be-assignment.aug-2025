from datetime import datetime, timezone
from enum import Enum
from sqlalchemy import String, DateTime, ForeignKey, Enum as PgEnum, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

class UserRole(str, Enum):
    """Global role inside the organization."""
    admin = "admin"
    manager = "manager"
    member = "member"

class User(Base):
    """A user who belongs to exactly one organization."""
    __tablename__ = "users"
    __table_args__ = (
        Index("ix_users_email_unique", "email", unique=True),  # required by review criteria
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    org_id: Mapped[int] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)

    email: Mapped[str] = mapped_column(String(255), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(PgEnum(UserRole, name="user_role"), default=UserRole.member, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    organization = relationship("Organization", back_populates="users")
    assigned_tasks: Mapped[list["Task"]] = relationship("Task", back_populates="assignee")
    notifications: Mapped[list["Notification"]] = relationship("Notification", back_populates="user")