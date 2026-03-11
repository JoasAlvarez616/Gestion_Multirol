from app.database import Base, engine
from app.models.user import User
from app.models.role import Role
from app.models.task import Task
from app.models.subtask import SubTask  

# Crear todas las tablas
Base.metadata.create_all(bind=engine)

print("Base de datos inicializada y tablas creadas correctamente")