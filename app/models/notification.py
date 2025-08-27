from datetime import datetime, timezone
from enum import Enum
from sqlalchemy import String, Text, Boolean, DateTime, ForeignKey, Enum as PgEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

class NotificationType(str, Enum):
    assignment = "assignment"         # user assigned to a task
    status_change = "status_change"   # task status updated
    comment_added = "comment_added"   # new comment on user's task

class Notification(Base):
    """A simple per-user notification stored in DB (can mirror to Redis)."""
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    type: Mapped[NotificationType] = mapped_column(PgEnum(NotificationType, name="notification_type"), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # optional linkage for convenience (not strictly required by spec)
    project_id: Mapped[int | None] = mapped_column(ForeignKey("projects.id", ondelete="SET NULL"))
    task_id: Mapped[int | None] = mapped_column(ForeignKey("tasks.id", ondelete="SET NULL"))

    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    user = relationship("User", back_populates="notifications")