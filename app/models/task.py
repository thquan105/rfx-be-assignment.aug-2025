from datetime import date, datetime, timezone
from enum import Enum

from sqlalchemy import Date, DateTime
from sqlalchemy import Enum as PgEnum
from sqlalchemy import ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class TaskStatus(str, Enum):
    todo = "todo"
    in_progress = "in-progress"
    done = "done"


class TaskPriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class Task(Base):
    """A task belongs to a project and may be assigned to a user."""

    __tablename__ = "tasks"
    __table_args__ = (
        Index(
            "ix_tasks_status_project", "status", "project_id"
        ),  # required by review criteria
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[TaskStatus] = mapped_column(
        PgEnum(TaskStatus, name="task_status"), default=TaskStatus.todo, nullable=False
    )
    priority: Mapped[TaskPriority] = mapped_column(
        PgEnum(TaskPriority, name="task_priority"),
        default=TaskPriority.medium,
        nullable=False,
    )
    due_date: Mapped[date | None] = mapped_column(Date)

    assignee_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL")
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    project = relationship("Project", back_populates="tasks")
    assignee = relationship("User", back_populates="assigned_tasks")
    comments: Mapped[list["Comment"]] = relationship(
        "Comment", back_populates="task", cascade="all,delete-orphan"
    )
    attachments: Mapped[list["Attachment"]] = relationship(
        "Attachment", back_populates="task", cascade="all,delete-orphan"
    )
