import os
from uuid import uuid4
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from app.config import settings
from app.repositories.attachment_repository import AttachmentRepository
from app.repositories.project_member_repository import ProjectMemberRepository
from app.models.task import Task
from app.models.user import User

class AttachmentService:
    @staticmethod
    def upload_attachment(db: Session, task: Task, user: User, file: UploadFile):
        # Permission: only project members can upload
        if not ProjectMemberRepository.is_member(db, task.project.id, user.id):
            raise HTTPException(status_code=403, detail="You are not a project member")

        contents = file.file.read()
        size = len(contents)

        # Validate
        if size > settings.max_file_size:
            raise HTTPException(status_code=400, detail="File too large")

        existing_count = len(task.attachments)
        if existing_count >= settings.max_files_per_task:
            raise HTTPException(status_code=400, detail="Max attachments reached")

        # Save file
        os.makedirs(settings.upload_dir, exist_ok=True)
        # Prevent path traversal and normalize filename
        safe_name = os.path.basename(file.filename or "")
        if not safe_name:
            raise HTTPException(status_code=400, detail="Invalid file name")

        # Generate unique stored filename: <random>_<original>
        unique_name = f"{uuid4().hex[-12:]}_{safe_name}"
        path = os.path.join(settings.upload_dir, unique_name)
        with open(path, "wb") as f:
            f.write(contents)

        # Persist original file_name, stored file_path, and size
        return AttachmentRepository.create(db, task.id, user.id, safe_name, path, size)

    @staticmethod
    def list_attachments(db: Session, task_id: int):
        return AttachmentRepository.list_by_task(db, task_id)
