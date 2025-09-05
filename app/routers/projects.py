from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_roles
from app.database import get_db
from app.repositories.project_member_repository import ProjectMemberRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.user_repository import UserRepository
from app.schemas.project import (ProjectAddMembersRequest, ProjectCreate,
                                 ProjectOut)
from app.schemas.user import UserOut

router = APIRouter()


@router.post("/projects", response_model=ProjectOut)
def create_project(
    payload: ProjectCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    project = ProjectRepository.create(
        db,
        name=payload.name,
        description=payload.description,
        org_id=current_user.org_id,
    )
    ProjectMemberRepository.add_member(
        db, project_id=project.id, user_id=current_user.id
    )
    return project


@router.get("/projects", response_model=list[ProjectOut])
def list_projects(
    db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    return ProjectRepository.list_by_org(db, current_user.org_id)


@router.get("/projects/{project_id}", response_model=ProjectOut)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    project = ProjectRepository.get_by_id(db, project_id)
    if not project or project.org_id != current_user.org_id:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("/projects/{project_id}/members", response_model=list[UserOut])
def add_project_members(
    project_id: int,
    payload: ProjectAddMembersRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "manager")),
):
    project = ProjectRepository.get_by_id(db, project_id)
    if not project or project.org_id != current_user.org_id:
        raise HTTPException(status_code=404, detail="Project not found")

    added_users = []
    for user_id in payload.user_ids:
        user = UserRepository.get_by_id(db, user_id)
        if not user or user.org_id != current_user.org_id:
            continue
        if not ProjectMemberRepository.is_member(db, project_id, user_id):
            ProjectMemberRepository.add_member(
                db, project_id=project_id, user_id=user_id
            )
            added_users.append(user)
    if not added_users:
        raise HTTPException(status_code=400, detail="No valid users added")
    return added_users


@router.delete("/projects/{project_id}/members/{user_id}", status_code=204)
def remove_project_member(
    project_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "manager")),
):
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot remove yourself")
    project = ProjectRepository.get_by_id(db, project_id)
    if not project or project.org_id != current_user.org_id:
        raise HTTPException(status_code=404, detail="Project not found")

    ProjectMemberRepository.remove_member(db, project_id=project_id, user_id=user_id)
    return


@router.get("/projects/{project_id}/members", response_model=list[UserOut])
def list_project_members(
    project_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    project = ProjectRepository.get_by_id(db, project_id)
    if not project or project.org_id != current_user.org_id:
        raise HTTPException(status_code=404, detail="Project not found")

    return ProjectMemberRepository.list_members(db, project_id=project_id)
