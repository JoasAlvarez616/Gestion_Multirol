from sqlalchemy import Table, Column, Integer, ForeignKey, String
from app.database.database import Base

context_members = Table(
    "context_members",
    Base.metadata,
    Column("user_id", Integer,
           ForeignKey("users.id"), primary_key=True),
    Column("context_id", Integer,
           ForeignKey("contexts.id"), primary_key=True),
    Column("role", String, default="member")
)