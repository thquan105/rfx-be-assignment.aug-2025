from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.task import TaskCreate, TaskUpdate, TaskOut
from app.repositories.task_repository import TaskRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.project_member_repository import ProjectMemberRepository
from app.repositories.user_repository import UserRepository
from app.core.deps import get_current_user
from app.models.task import TaskStatus, TaskPriority
from app.services.notification_service import NotificationService

router = APIRouter()

@router.post("/projects/{project_id}/tasks", response_model=TaskOut)
def create_task(project_id: int, payload: TaskCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    project = ProjectRepository.get_by_id(db, project_id)
    if not project or project.org_id != current_user.org_id:
        raise HTTPException(status_code=404, detail="Project not found")
    if not ProjectMemberRepository.is_member(db, project_id, current_user.id):
        raise HTTPException(status_code=403, detail="You are not a project member")    
    if current_user.role.value == "member":
        raise HTTPException(status_code=403, detail="Members cannot create tasks")

    # Assignee validation
    assignee = None
    if payload.assignee_id is not None:
        if current_user.role.value == "member":
            raise HTTPException(status_code=403, detail="Only Admin/Manager can assign tasks to others")
        assignee = UserRepository.get_by_id(db, payload.assignee_id)
        if not assignee or assignee.org_id != current_user.org_id:
            raise HTTPException(status_code=404, detail="Assignee not found")
        
    task = TaskRepository.create(db, project_id, payload)
    
    # Notification
    if assignee:
        NotificationService.create_assignment_notification(db, task, assignee)

    return task

@router.get("/projects/{project_id}/tasks", response_model=list[TaskOut])
def list_tasks(project_id: int, status: TaskStatus | None = None, assignee_id: int | None = None, priority: TaskPriority | None = None, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    project = ProjectRepository.get_by_id(db, project_id)
    if not project or project.org_id != current_user.org_id:
        raise HTTPException(status_code=404, detail="Project not found")
    if not ProjectMemberRepository.is_member(db, project_id, current_user.id):
        raise HTTPException(status_code=403, detail="You are not a project member")

    return TaskRepository.list_by_project(db, project_id, status, assignee_id, priority)

@router.get("/tasks/{task_id}", response_model=TaskOut)
def get_task(task_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    task = TaskRepository.get_by_id(db, task_id)
    if not task or task.project.org_id != current_user.org_id:
        raise HTTPException(status_code=404, detail="Task not found")
    if not ProjectMemberRepository.is_member(db, task.project_id, current_user.id):
        raise HTTPException(status_code=403, detail="You are not a project member")
    return task

@router.patch("/tasks/{task_id}", response_model=TaskOut)
def update_task(task_id: int, payload: TaskUpdate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    task = TaskRepository.get_by_id(db, task_id)
    if not task or task.project.org_id != current_user.org_id:
        raise HTTPException(status_code=404, detail="Task not found")
    if not ProjectMemberRepository.is_member(db, task.project_id, current_user.id):
        raise HTTPException(status_code=403, detail="You are not a project member")
    if current_user.role.value == "member":
        if any(
            getattr(payload, field) is not None
            for field in ["title", "description", "priority", "due_date", "assignee_id"]
        ):
            raise HTTPException(status_code=403, detail="Members can only update status")
    # Assignee check
    assignee = None
    old_assignee_id = task.assignee_id
    old_status_value = task.status.value
    if payload.assignee_id is not None:
        if current_user.role.value == "member":
            raise HTTPException(status_code=403, detail="Only Admin/Manager can assign tasks to others")
        assignee = UserRepository.get_by_id(db, payload.assignee_id)
        if not assignee or assignee.org_id != current_user.org_id:
            raise HTTPException(status_code=404, detail="Assignee not found")

    # Status progression check
    status_order = {"todo": 1, "in-progress": 2, "done": 3}
    if payload.status:
        if status_order[payload.status.value] < status_order[task.status.value]:
            raise HTTPException(status_code=400, detail="Status cannot move backward")
        NotificationService.create_status_change_notification(db, task)
        
    task = TaskRepository.update(db, task, payload)

    # Notifications
    if assignee and task.assignee_id != old_assignee_id:
        NotificationService.create_assignment_notification(db, task, assignee)

    if payload.status is not None and task.status.value != old_status_value:
        NotificationService.create_status_change_notification(db, task)

    return task
