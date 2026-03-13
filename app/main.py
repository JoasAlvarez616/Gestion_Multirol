from fastapi import FastAPI
from app.routers import user
from app.database.database import engine, Base
from app import models

app = FastAPI(
    title="Sistema de Gestion Multirol",
    version="0.1.0",
    description= ( "Una aplicación para gestionar múltiples roles y tareas de usuario de un sistema. "
    "Permite a los usuarios crear, editar y eliminar tareas. "
    "También incluye un sistema de notificaciones para mantener a los usuarios informados sobre las tareas asignadas y su progreso."),
)

Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"message": "Bienvenido al Sistema de Gestion Multirol"}

app.include_router(user.router)