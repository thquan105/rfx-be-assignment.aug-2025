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

router = APIRouter()

@router.post("/projects/{project_id}/tasks", response_model=TaskOut)
def create_task(project_id: int, payload: TaskCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    project = ProjectRepository.get_by_id(db, project_id)
    if not project or project.org_id != current_user.org_id:
        raise HTTPException(status_code=404, detail="Project not found")
    if not ProjectMemberRepository.is_member(db, project_id, current_user.id):
        raise HTTPException(status_code=403, detail="You are not a project member")

    # Assignee validation
    if payload.assignee_id is not None:
        if payload.assignee_id != current_user.id and current_user.role.value not in ("admin", "manager"):
            raise HTTPException(status_code=403, detail="You can only assign tasks to yourself")
        assignee = UserRepository.get_by_id(db, payload.assignee_id)
        if not assignee or assignee.org_id != current_user.org_id:
            raise HTTPException(status_code=404, detail="Assignee not found")

    return TaskRepository.create(db, project_id, payload)

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

    # Assignee check
    if payload.assignee_id is not None:
        if payload.assignee_id != current_user.id and current_user.role.value not in ("admin", "manager"):
            raise HTTPException(status_code=403, detail="You can only assign to yourself")
        assignee = UserRepository.get_by_id(db, payload.assignee_id)
        if not assignee or assignee.org_id != current_user.org_id:
            raise HTTPException(status_code=404, detail="Assignee not found")

    # Status progression check
    status_order = {"todo": 1, "in-progress": 2, "done": 3}
    if payload.status:
        if status_order[payload.status.value] < status_order[task.status.value]:
            raise HTTPException(status_code=400, detail="Status cannot move backward")

    return TaskRepository.update(db, task, payload)
