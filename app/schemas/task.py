# app/schemas/task.py
from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import date
from app.models.task import TaskStatus, TaskPriority

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    assignee_id: Optional[int] = None  # validate in logic
    priority: TaskPriority = TaskPriority.medium
    due_date: Optional[date] = None

    @field_validator("due_date")
    @classmethod
    def validate_due_date(cls, v):
        if v is not None and v < date.today():
            raise ValueError("Due date cannot be in the past")
        return v

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    assignee_id: Optional[int] = None
    priority: Optional[TaskPriority] = None
    status: Optional[TaskStatus] = None
    due_date: Optional[date] = None

    @field_validator("due_date")
    @classmethod
    def validate_due_date(cls, v):
        if v is not None and v < date.today():
            raise ValueError("Due date cannot be in the past")
        return v

class TaskOut(BaseModel):
    id: int
    project_id: int
    title: str
    description: Optional[str]
    assignee_id: Optional[int]
    priority: TaskPriority
    status: TaskStatus
    due_date: Optional[date]

    model_config = {
        "from_attributes": True
    }
