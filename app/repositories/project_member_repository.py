from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.project import ProjectMember
from app.models.user import User


class ProjectMemberRepository:
    @staticmethod
    def add_member(db: Session, *, project_id: int, user_id: int):
        member = ProjectMember(project_id=project_id, user_id=user_id)
        db.add(member)
        db.commit()
        db.refresh(member)
        return member

    @staticmethod
    def remove_member(db: Session, *, project_id: int, user_id: int):
        stmt = delete(ProjectMember).where(
            ProjectMember.project_id == project_id, ProjectMember.user_id == user_id
        )
        db.execute(stmt)
        db.commit()

    @staticmethod
    def list_members(db: Session, project_id: int) -> list[User]:
        stmt = (
            select(User)
            .join(ProjectMember, ProjectMember.user_id == User.id)
            .where(ProjectMember.project_id == project_id)
        )
        return list(db.execute(stmt).scalars().all())

    @staticmethod
    def is_member(db: Session, project_id: int, user_id: int) -> bool:
        stmt = select(ProjectMember).where(
            ProjectMember.project_id == project_id, ProjectMember.user_id == user_id
        )
        return db.execute(stmt).scalar_one_or_none() is not None
