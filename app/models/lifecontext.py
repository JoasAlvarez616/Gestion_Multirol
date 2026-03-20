from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, UniqueConstraint
from datetime import datetime, timezone
from sqlalchemy.orm import relationship
from app.database.database import Base

class LifeContext(Base):
    __tablename__ = "contexts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    owner = relationship(
        "User",
        back_populates="owned_contexts")

    members = relationship(
        "User",
        secondary="context_members",
        back_populates="member_contexts")

    tasks = relationship(
        "Task",
        back_populates="context")
