from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.task import Task
from app.models.user import User
from app.repositories.comment_repository import CommentRepository
from app.repositories.project_member_repository import ProjectMemberRepository
from app.schemas.comment import CommentCreate
from app.services.notification_service import NotificationService


class CommentService:
    @staticmethod
    def add_comment(db: Session, task: Task, user: User, comment_in: CommentCreate):
        # Permission: only project members can upload
        if not ProjectMemberRepository.is_member(db, task.project.id, user.id):
            raise HTTPException(status_code=403, detail="You are not a project member")

        comment = CommentRepository.create(db, task.id, user.id, comment_in.content)

        # Notification
        NotificationService.create_comment_notification(db, task, user)

        return comment

    @staticmethod
    def list_comments(db: Session, task_id: int):
        return CommentRepository.list_by_task(db, task_id)
