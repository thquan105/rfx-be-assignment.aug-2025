from pydantic import BaseModel
from datetime import date

class TaskStatusCount(BaseModel):
    todo: int | None = 0
    in_progress: int | None = 0
    done: int | None = 0

class OverdueTaskOut(BaseModel):
    id: int
    title: str
    due_date: date
    status: str

    class Config:
        orm_mode = True
