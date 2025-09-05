from datetime import datetime

from pydantic import BaseModel

from app.models.notification import NotificationType


class NotificationRead(BaseModel):
    id: int
    type: NotificationType
    message: str
    is_read: bool
    project_id: int | None
    task_id: int | None
    created_at: datetime

    model_config = {"from_attributes": True}
