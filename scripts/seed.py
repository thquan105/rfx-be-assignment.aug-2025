"""
Seed the database with development data.

Usage: python scripts/seed.py
"""

from __future__ import annotations
from datetime import date, timedelta
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.organization import Organization
from app.models.user import User, UserRole
from app.models.project import Project, ProjectMember
from app.models.task import Task, TaskPriority, TaskStatus
from app.models.comment import Comment
from app.utils.security import hash_password


def get_or_create_org(db: Session, name: str) -> Organization:
    org = db.query(Organization).filter(Organization.name == name).one_or_none()
    if org:
        return org
    org = Organization(name=name)
    db.add(org)
    db.commit()
    db.refresh(org)
    return org


def get_or_create_user(
    db: Session, org_id: int, email: str, role: UserRole, password: str, full_name: str | None = None
) -> User:
    user = db.query(User).filter(User.email == email).one_or_none()
    if user:
        return user
    user = User(
        org_id=org_id,
        email=email,
        password_hash=hash_password(password),
        full_name=full_name,
        role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_or_create_project(db: Session, org_id: int, name: str, description: str | None = None) -> Project:
    project = db.query(Project).filter(Project.org_id == org_id, Project.name == name).one_or_none()
    if project:
        return project
    project = Project(org_id=org_id, name=name, description=description)
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def ensure_project_member(db: Session, project_id: int, user_id: int) -> None:
    exists = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id, ProjectMember.user_id == user_id
    ).one_or_none()
    if exists is None:
        db.add(ProjectMember(project_id=project_id, user_id=user_id))
        db.commit()


def seed_tasks_and_comments(db: Session, project: Project, assignees: list[User]) -> None:
    """
    Seed 1 task cho mỗi assignee, cộng thêm task overdue + 1 comment.
    """
    if db.query(Task).filter(Task.project_id == project.id).count() > 0:
        return

    today = date.today()
    tasks = []

    for i, assignee in enumerate(assignees):
        task = Task(
            project_id=project.id,
            title=f"Task {i+1} for {assignee.full_name or assignee.email}",
            description="Auto-seeded task",
            status=[TaskStatus.todo, TaskStatus.in_progress, TaskStatus.done][i % 3],
            priority=[TaskPriority.low, TaskPriority.medium, TaskPriority.high][i % 3],
            assignee_id=assignee.id,
            due_date=today + timedelta(days=(i + 1) * 3),
        )
        tasks.append(task)

    # Thêm 1 task overdue cho assignee đầu tiên
    tasks.append(
        Task(
            project_id=project.id,
            title="Overdue Task",
            description="This task is overdue",
            status=TaskStatus.todo,
            priority=TaskPriority.high,
            assignee_id=assignees[0].id,
            due_date=today - timedelta(days=5),
        )
    )

    db.add_all(tasks)
    db.commit()

    # Comment mẫu: assignee[1] comment vào task[0]
    if len(assignees) > 1:
        db.add(
            Comment(
                task_id=tasks[0].id,
                user_id=assignees[1].id,
                content="I can pick this up next.",
            )
        )
        db.commit()


def main() -> int:
    db = SessionLocal()
    try:
        print("[seed] Creating base data...")

        # Orgs
        org1 = get_or_create_org(db, "RFX DN")
        org2 = get_or_create_org(db, "OtherOrg")

        # Users for org1
        admin = get_or_create_user(db, org1.id, "admin@example.com", UserRole.admin, "password", "Admin User")
        manager = get_or_create_user(db, org1.id, "manager@example.com", UserRole.manager, "password", "Manager User")

        member0 = get_or_create_user(db, org1.id, "member0@example.com", UserRole.member, "password", "Member 0")
        member1 = get_or_create_user(db, org1.id, "member1@example.com", UserRole.member, "password", "Member 1")
        member2 = get_or_create_user(db, org1.id, "member2@example.com", UserRole.member, "password", "Member 2")
        member3 = get_or_create_user(db, org1.id, "member3@example.com", UserRole.member, "password", "Member 3")
        member4 = get_or_create_user(db, org1.id, "member4@example.com", UserRole.member, "password", "Member 4")
        member5 = get_or_create_user(db, org1.id, "member5@example.com", UserRole.member, "password", "Member 5")

        # Users for org2 (OtherOrg)
        other_admin = get_or_create_user(db, org2.id, "otheradmin@example.com", UserRole.admin, "password", "OtherOrg Admin")
        other_manager = get_or_create_user(db, org2.id, "othermanager@example.com", UserRole.manager, "password", "OtherOrg Manager")
        other_member1 = get_or_create_user(db, org2.id, "othermember1@example.com", UserRole.member, "password", "Other Member 1")
        other_member2 = get_or_create_user(db, org2.id, "othermember2@example.com", UserRole.member, "password", "Other Member 2")
        other_member3 = get_or_create_user(db, org2.id, "othermember3@example.com", UserRole.member, "password", "Other Member 3")

        # Projects
        project_a = get_or_create_project(db, org1.id, "Demo Project", "Main demo project with core members")
        project_b = get_or_create_project(db, org1.id, "Side Project", "Side project with other members")

        # Add members
        for u in (admin, manager, member0, member1, member2):
            ensure_project_member(db, project_a.id, u.id)
        for u in (admin, member3, member4, member5):
            ensure_project_member(db, project_b.id, u.id)

        # Tasks + comments (mỗi member ít nhất 1 task)
        seed_tasks_and_comments(db, project_a, [member0, member1, member2])
        seed_tasks_and_comments(db, project_b, [member3, member4, member5])

        print("[seed] Seeding completed.")
        return 0
    except Exception as e:
        db.rollback()
        print(f"[seed] Error: {e}")
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
