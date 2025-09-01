from sqlalchemy.orm import Session
from app.models.attachment import Attachment

class AttachmentRepository:
    @staticmethod
    def create(db: Session, task_id: int, user_id: int, file_name: str, file_path: str, file_size: int) -> Attachment:
        att = Attachment(task_id=task_id, user_id=user_id, file_name=file_name, file_path=file_path, file_size=file_size)
        db.add(att)
        db.commit()
        db.refresh(att)
        return att

    @staticmethod
    def list_by_task(db: Session, task_id: int) -> list[Attachment]:
        return db.query(Attachment).filter(Attachment.task_id == task_id).all()
