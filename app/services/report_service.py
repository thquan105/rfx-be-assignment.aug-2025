from datetime import date
from sqlalchemy.orm import Session
from app.repositories.report_repository import ReportRepository

class ReportService:
    @staticmethod
    def status_count(db: Session, project_id: int):
        return ReportRepository.count_tasks_by_status(db, project_id)

    @staticmethod
    def overdue_tasks(db: Session, project_id: int):
        today = date.today()
        return ReportRepository.get_overdue_tasks(db, project_id, today)
