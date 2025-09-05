from typing import List, Optional

from pydantic import BaseModel


class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None


class ProjectOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    org_id: int

    model_config = {"from_attributes": True}


class ProjectAddMembersRequest(BaseModel):
    user_ids: List[int]
