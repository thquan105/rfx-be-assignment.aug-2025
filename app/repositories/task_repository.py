from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.task import Task, TaskPriority, TaskStatus
from app.schemas.task import TaskCreate, TaskUpdate


class TaskRepository:
    @staticmethod
    def create(db: Session, project_id: int, payload: TaskCreate) -> Task:
        task = Task(
            project_id=project_id,
            title=payload.title,
            description=payload.description,
            assignee_id=payload.assignee_id,
            priority=payload.priority,
            due_date=payload.due_date,
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        return task

    @staticmethod
    def get_by_id(db: Session, task_id: int) -> Task | None:
        return db.get(Task, task_id)

    @staticmethod
    def list_by_project(
        db: Session,
        project_id: int,
        status: TaskStatus | None = None,
        assignee_id: int | None = None,
        priority: TaskPriority | None = None,
    ) -> list[Task]:
        stmt = select(Task).where(Task.project_id == project_id)

        if status:
            stmt = stmt.where(Task.status == status)
        if assignee_id:
            stmt = stmt.where(Task.assignee_id == assignee_id)
        if priority:
            stmt = stmt.where(Task.priority == priority)

        return list(db.execute(stmt).scalars().all())

    @staticmethod
    def update(db: Session, task: Task, payload: TaskUpdate) -> Task:
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(task, field, value)
        db.commit()
        db.refresh(task)
        return task
