from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, UniqueConstraint
from datetime import datetime, timezone
from sqlalchemy.orm import relationship
from app.database.database import Base

class LifeContext(Base):
    __tablename__ = "contexts"

    __table_args__ = (
        UniqueConstraint('user_id', 'name', name='unique_context_per_user'),
        )


    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    user = relationship("User", back_populates="contexts")

    tasks = relationship("Task", back_populates="context", cascade="all, delete-orphan")