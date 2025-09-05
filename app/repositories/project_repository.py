from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.project import Project


class ProjectRepository:
    @staticmethod
    def create(
        db: Session, *, name: str, description: str | None, org_id: int
    ) -> Project:
        project = Project(name=name, description=description, org_id=org_id)
        db.add(project)
        db.commit()
        db.refresh(project)
        return project

    @staticmethod
    def get_by_id(db: Session, project_id: int) -> Project | None:
        return db.get(Project, project_id)

    @staticmethod
    def list_by_org(db: Session, org_id: int) -> list[Project]:
        stmt = select(Project).where(Project.org_id == org_id)
        return list(db.execute(stmt).scalars().all())
