from pydantic import BaseModel
from typing import Optional, Union, List
from datetime import datetime, date
from enum import Enum

class TaskStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"

class TaskPriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    priority: TaskPriority = TaskPriority.medium
    due_date: Optional[Union[datetime, date]] = None

class TaskCreate(TaskBase):
    context_id: int

class TaskUpdateStatus(BaseModel):
    status: TaskStatus

class TaskResponse(TaskBase):
    id: int
    status: TaskStatus
    context_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[Union[datetime, date]] = None

    class Config:
        from_attributes = True


class TodayDashboardResponse(BaseModel):
    overdue: List[TaskResponse]
    today: List[TaskResponse]

    class Config:
        from_attributes = True


class DashboardSummaryResponse(BaseModel):
    overdue: int
    today: int
    upcoming: int
    total_pending: int
    completed_today: int