from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database.database import get_db
from app.models.subtask import SubTask
from app.models.task import Task
from app.models.lifecontext import LifeContext
from app.routers.user import get_current_user
from app.models.user import User
from app.schemas.subtask import SubtaskCreate, SubtaskResponse
from app.security.dependencies import get_current_user

router = APIRouter(
    prefix="/subtasks",
    tags=["subtasks"],
)


"""
Creamos una subtarea asociada a una tarea existente, verificando que la tarea pertenece al usuario actual.
Si la tarea no existe o no pertenece al usuario, se devuelve un error 403.
"""
@router.post("/", response_model=SubtaskResponse)
def create_subtask(
        subtask: SubtaskCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)):

    # Verificar que la tarea existe y pertenece al usuario
    task = db.query(Task)\
        .join(LifeContext)\
            .filter(Task.id == subtask.task_id,
        LifeContext.user_id == current_user.id)\
            .first()

    if not task:
        raise HTTPException(status_code=403, detail="No puede crear subtareas para esta tarea")

   # Crear la subtarea
    db_subtask = SubTask(
        title=subtask.title,
        task_id=subtask.task_id
    )

    db.add(db_subtask)
    db.commit()
    db.refresh(db_subtask)
    return db_subtask


"""
Obtenemos las subtareas del usuario actual, con paginación.
Solo se devuelven las subtareas que pertenecen a las tareas de los contextos del usuario.
"""
@router.get("/", response_model=List[SubtaskResponse])
def get_subtasks(
    skip: int = 0, limit: int = 10,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)):

    subtasks = db.query(SubTask)\
        .join(Task)\
        .join(LifeContext)\
        .filter(LifeContext.user_id == current_user.id)\
        .offset(skip)\
            .limit(limit)\
                .all()
    return subtasks


"""
Obtenemos una subtarea específica por su ID, verificando que pertenece al usuario actual.
Si la subtarea no existe o no pertenece al usuario, se devuelve un error 404.
"""
@router.get("/{subtask_id}", response_model=SubtaskResponse)
def get_subtask(
    subtask_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)):

    subtask = db.query(SubTask)\
        .join(Task)\
        .join(LifeContext)\
        .filter(SubTask.id == subtask_id,
                LifeContext.user_id == current_user.id)\
        .first()

    if not subtask:
        raise HTTPException(status_code=404, detail="Subtarea no encontrada o no tiene acceso")
    return subtask


"""
Eliminamos una subtarea específica por su ID, verificando que pertenece al usuario actual.
Si la subtarea no existe o no pertenece al usuario, se devuelve un error 404.
"""
@router.delete("/{subtask_id}")
def delete_subtask(
    subtask_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)):

    subtask = db.query(SubTask)\
        .join(Task)\
        .join(LifeContext)\
        .filter(SubTask.id == subtask_id,
                LifeContext.user_id == current_user.id)\
        .first()
    
    if not subtask:
        raise HTTPException(status_code=404, detail="Subtarea no encontrada o no tiene acceso")

    db.delete(subtask)
    db.commit()
    return {"detail": "Subtarea eliminada exitosamente"}