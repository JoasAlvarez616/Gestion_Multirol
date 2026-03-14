from pydantic import BaseModel
from datetime import datetime

class SubtaskBase(BaseModel):
    title: str

class SubtaskCreate(SubtaskBase):
    task_id: int

class SubtaskResponse(SubtaskBase):
    id: int
    task_id: int
    is_completed: bool
    created_at: datetime

    class Config:
        from_attributes = True