from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.organization import Organization


class OrganizationRepository:
    @staticmethod
    def get_by_name(db: Session, name: str) -> Organization | None:
        stmt = select(Organization).where(Organization.name == name)
        return db.execute(stmt).scalar_one_or_none()

    @staticmethod
    def create(db: Session, name: str) -> Organization:
        org = Organization(name=name)
        db.add(org)
        db.flush()
        return org
