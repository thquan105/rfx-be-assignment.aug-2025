from sqlalchemy.orm import Session

from app.models.notification import NotificationType
from app.models.task import Task
from app.models.user import User
from app.repositories.notification_repository import NotificationRepository


class NotificationService:
    @staticmethod
    def create_assignment_notification(db: Session, task: Task, assignee: User):
        return NotificationRepository.create(
            db,
            user_id=assignee.id,
            notif_type=NotificationType.assignment,
            message=f"You have been assigned to task '{task.title}'",
            project_id=task.project_id,
            task_id=task.id,
        )

    @staticmethod
    def create_status_change_notification(db: Session, task: Task):
        if task.assignee_id:
            return NotificationRepository.create(
                db,
                user_id=task.assignee_id,
                notif_type=NotificationType.status_change,
                message=f"Task '{task.title}' status changed to {task.status}",
                project_id=task.project_id,
                task_id=task.id,
            )

    @staticmethod
    def create_comment_notification(db: Session, task: Task, commenter: User):
        if task.assignee_id and task.assignee_id != commenter.id:
            return NotificationRepository.create(
                db,
                user_id=task.assignee_id,
                notif_type=NotificationType.comment_added,
                message=f"New comment on task '{task.title}'",
                project_id=task.project_id,
                task_id=task.id,
            )

    @staticmethod
    def get_unread(db: Session, user: User):
        return NotificationRepository.get_unread(db, user.id)

    @staticmethod
    def mark_read(db: Session, notif_id: int, user: User):
        return NotificationRepository.mark_read(db, notif_id, user.id)

    @staticmethod
    def mark_all_read(db: Session, user: User):
        return NotificationRepository.mark_all_read(db, user.id)
