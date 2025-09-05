from datetime import datetime

from pydantic import BaseModel


class AttachmentRead(BaseModel):
    id: int
    user_id: int
    file_name: str
    file_path: str
    file_size: int
    created_at: datetime

    model_config = {"from_attributes": True}
