from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.report_service import ReportService
from app.schemas.report import TaskStatusCount, OverdueTaskOut
from app.models.project import Project
from app.core.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/projects/{project_id}/report", tags=["Reports"])

def check_report_permission(current_user: User):
    if current_user.role.value not in ("admin", "manager"):
        raise HTTPException(status_code=403, detail="Only Admin/Manager can access reports")

@router.get("/status-count", response_model=TaskStatusCount)
def get_status_count(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    check_report_permission(current_user)

    project = db.query(Project).filter(
        Project.id == project_id, Project.org_id == current_user.org_id
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return ReportService.status_count(db, project_id)

@router.get("/overdue-tasks", response_model=list[OverdueTaskOut])
def get_overdue_tasks(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    check_report_permission(current_user)

    project = db.query(Project).filter(
        Project.id == project_id, Project.org_id == current_user.org_id
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return ReportService.overdue_tasks(db, project_id)
