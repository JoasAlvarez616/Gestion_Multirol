from fastapi import FastAPI
from app.database.database import Base, engine
from app.routers import user, auth, lifecontext, task, subtask
from app.models.user import User
from app.models.lifecontext import LifeContext
from app.models.task import Task
from app.models.tag import Tag
from app.models.subtask import SubTask
from app.models.task_tag import task_tags
from app.models.context_member import context_members

# ==============================
# Inicializar FastAPI
# ==============================
app = FastAPI(
    title="Sistema de Gestion Multirol",
    version="0.1.0",
    description=(
        "Una aplicación para gestionar múltiples roles y tareas de usuario de un sistema. "
        "Permite a los usuarios crear, editar y eliminar tareas. "
        "También incluye un sistema de notificaciones para mantener a los usuarios informados sobre las tareas asignadas y su progreso."
    ),
)

# Crear tablas si no existen
Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"message": "Bienvenido al Sistema de Gestion Multirol"}


# ==============================
# Routers
# ==============================
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(lifecontext.router)
app.include_router(task.router)
app.include_router(subtask.router)
