from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class LifeContextBase(BaseModel):
    name: str
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class LifeContextCreate(LifeContextBase):
    pass

class LifeContextResponse(LifeContextBase):
    id: int
    owner_id: int
    created_at: datetime

    class Config:
        from_attributes = True