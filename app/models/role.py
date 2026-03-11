from app.database.database import Base
from app.models.user import User
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relación con User
    user = relationship("User", back_populates="roles")
    # Relación con Task
    tasks = relationship("Task", back_populates="role", cascade="all, delete-orphan")