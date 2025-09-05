from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database import get_db
from app.models.task import Task
from app.repositories.project_member_repository import ProjectMemberRepository
from app.schemas.comment import CommentCreate, CommentRead
from app.services.comment_service import CommentService

router = APIRouter()


@router.post("/tasks/{task_id}/comments", response_model=CommentRead)
def add_comment(
    task_id: int,
    comment_in: CommentCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    try:
        return CommentService.add_comment(db, task, current_user, comment_in)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.get("/tasks/{task_id}/comments", response_model=list[CommentRead])
def list_comments(
    task_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if not ProjectMemberRepository.is_member(db, task.project_id, current_user.id):
        raise HTTPException(status_code=403, detail="You are not a project member")
    return CommentService.list_comments(db, task_id)
