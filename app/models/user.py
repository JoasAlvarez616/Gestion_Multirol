from app.database.database import Base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    ownedr = relationship(
        "User",
        back_populates="owned_contexts")

    members = relationship(
        "User",
        secondary="context_members",
        back_populates="member_contexts")

    tasks = relationship(
        "Task",
        back_populates="context")