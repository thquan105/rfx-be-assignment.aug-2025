from pydantic import BaseModel

class OrgOut(BaseModel):
    id: int
    name: str

    model_config = {
        "from_attributes": True
    }