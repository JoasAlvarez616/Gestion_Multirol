from sqlalchemy import Table, Column, Integer, ForeignKey
from app.database.database import Base

# Tabla de asociación para la relación muchos a muchos entre Task y Tag
task_tags = Table(
        'task_tags',
        Base.metadata,
        Column('task_id', Integer, ForeignKey('tasks.id'), primary_key=True),
        Column('tag_id', Integer, ForeignKey('tags.id'), primary_key=True)
        )