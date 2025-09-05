from sqlalchemy.orm import Session

from app.models.notification import Notification, NotificationType


class NotificationRepository:
    @staticmethod
    def create(
        db: Session,
        user_id: int,
        notif_type: NotificationType,
        message: str,
        project_id: int | None = None,
        task_id: int | None = None,
    ) -> Notification:
        notif = Notification(
            user_id=user_id,
            type=notif_type,
            message=message,
            project_id=project_id,
            task_id=task_id,
        )
        db.add(notif)
        db.commit()
        db.refresh(notif)
        return notif

    @staticmethod
    def get_unread(db: Session, user_id: int) -> list[Notification]:
        return (
            db.query(Notification)
            .filter(Notification.user_id == user_id, Notification.is_read == False)
            .order_by(Notification.created_at.desc())
            .all()
        )

    @staticmethod
    def mark_read(db: Session, notif_id: int, user_id: int) -> Notification | None:
        notif = (
            db.query(Notification)
            .filter(Notification.id == notif_id, Notification.user_id == user_id)
            .first()
        )
        if notif:
            notif.is_read = True
            db.commit()
            db.refresh(notif)
        return notif

    @staticmethod
    def mark_all_read(db: Session, user_id: int) -> int:
        result = (
            db.query(Notification)
            .filter(Notification.user_id == user_id, Notification.is_read == False)
            .update({"is_read": True})
        )
        db.commit()
        return result
