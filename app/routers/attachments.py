from fastapi import APIRouter, Depends, UploadFile, HTTPException, File
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.attachment import AttachmentRead
from app.services.attachment_service import AttachmentService
from app.models.task import Task
from app.core.deps import get_current_user
from app.repositories.project_member_repository import ProjectMemberRepository

router = APIRouter()

@router.post("/tasks/{task_id}/attachments", response_model=AttachmentRead)
def upload_attachment(task_id: int, file: UploadFile = File(...), db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    try:
        return AttachmentService.upload_attachment(db, task, current_user, file)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))

@router.get("/tasks/{task_id}/attachments", response_model=list[AttachmentRead])
def list_attachments(task_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if not ProjectMemberRepository.is_member(db, task.project_id, current_user.id):
        raise HTTPException(status_code=403, detail="You are not a project member")
    return AttachmentService.list_attachments(db, task_id)
