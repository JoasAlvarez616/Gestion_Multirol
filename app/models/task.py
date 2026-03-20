# app/models/task.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database.database import Base
from app.models.lifecontext import LifeContext
import enum

# Enums para status y priority
class TaskStatus(enum.Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"

class TaskPriority(enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"

class Task(Base):
    __tablename__ = "tasks"

    __table_args__ = (UniqueConstraint('context_id', 'context_task_number', name='unique_task_number_per_context'),)

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    status = Column(Enum(TaskStatus), default=TaskStatus.pending, index=True)
    priority = Column(Enum(TaskPriority), default=TaskPriority.medium)
    start_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    due_date = Column(DateTime, nullable=True, index=True)
    context_id = Column(Integer, ForeignKey("contexts.id"), nullable=False, index=True)
    context_task_number = Column(Integer, nullable=False)  # Número de tarea dentro del contexto
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relación con Context
    context = relationship("LifeContext", back_populates="tasks")

    # Relación con SubTasks
    subtasks = relationship("SubTask", back_populates="task", cascade="all, delete-orphan")

    # Relación con Tags a través de la tabla de asociación task_tags
    tags = relationship("Tag", secondary="task_tags", back_populates="tasks")