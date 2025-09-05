from datetime import datetime, timezone

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Organization(Base):
    """An organization that owns projects and users."""

    __tablename__ = "organizations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    users: Mapped[list["User"]] = relationship(
        "User", back_populates="organization", cascade="all,delete-orphan"
    )
    projects: Mapped[list["Project"]] = relationship(
        "Project", back_populates="organization", cascade="all,delete-orphan"
    )
