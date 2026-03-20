from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database.database import Base

class Tag(Base):
    __tablename__ = 'tags'

    __table_args__ = (UniqueConstraint("user_id", "name",
    name="unique_tag_name_per_user"),
    )

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    color = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"),
                     nullable=False, index=True)

    # Establece la relación con el modelo User
    user = relationship("User", back_populates="tags")

    # Establece la relación con el modelo Task a través de la tabla de asociación task_tags
    tasks = relationship("Task", secondary="task_tags", back_populates="tags")


