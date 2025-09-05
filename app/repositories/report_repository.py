from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.task import Task


class ReportRepository:
    @staticmethod
    def count_tasks_by_status(db: Session, project_id: int):
        rows = (
            db.query(Task.status, func.count(Task.id))
            .filter(Task.project_id == project_id)
            .group_by(Task.status)
            .all()
        )
        return {status.value: count for status, count in rows}

    @staticmethod
    def get_overdue_tasks(db: Session, project_id: int, today):
        return (
            db.query(Task)
            .filter(
                Task.project_id == project_id,
                Task.due_date < today,
                Task.status != "done",
            )
            .all()
        )
