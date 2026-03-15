from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SubtaskBase(BaseModel):
    title: str
    is_completed: Optional[bool] = False


class SubtaskCreate(SubtaskBase):
    task_id: int

class SubtaskResponse(SubtaskBase):
    id: int
    task_id: int
    created_at: datetime

    class Config:
        from_attributes = True