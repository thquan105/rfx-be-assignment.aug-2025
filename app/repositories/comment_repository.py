from sqlalchemy.orm import Session

from app.models.comment import Comment


class CommentRepository:
    @staticmethod
    def create(db: Session, task_id: int, user_id: int, content: str) -> Comment:
        comment = Comment(task_id=task_id, user_id=user_id, content=content)
        db.add(comment)
        db.commit()
        db.refresh(comment)
        return comment

    @staticmethod
    def list_by_task(db: Session, task_id: int) -> list[Comment]:
        return (
            db.query(Comment)
            .filter(Comment.task_id == task_id)
            .order_by(Comment.created_at.asc())
            .all()
        )
