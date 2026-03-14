from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database.database import get_db
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskResponse
from app.models.user import User
from app.models.lifecontext import LifeContext
from app.security.dependencies import get_current_user

router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
)

@router.post("/", response_model=TaskResponse)
def create_task(
        task: TaskCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)):

    # Verificar que el contexto de vida existe y pertenece al usuario
    context = db.query(LifeContext).filter(
        LifeContext.id == task.context_id,
        LifeContext.user_id == current_user.id).first()

    if not context:
        raise HTTPException(status_code=404, detail="No puedes crear tareas en este contexto")

    # Crear la tarea
    db_task = Task(
        title=task.title,
        description=task.description,
        status=task.status,
        priority=task.priority,
        start_date=task.start_date,
        due_date=task.due_date,
        context_id=task.context_id
    )

    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


"""
Obtenemos las tareas del usuario actual, con paginación. 
Solo se devuelven las tareas que pertenecen a los contextos del usuario.
"""
@router.get("/", response_model=List[TaskResponse])
def get_tasks(
    skip: int = 0, limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)):

    tasks = db.query(Task)\
        .join(LifeContext)\
            .filter(LifeContext.user_id == current_user.id)\
                .offset(skip)\
                    .limit(limit).all()

    return tasks


"""
Obtenemos una tarea específica por su ID, verificando que pertenece al usuario actual.
Si la tarea no existe o no pertenece al usuario, se devuelve un error 404.
"""
@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)):

    task = db.query(Task)\
        .join(LifeContext)\
            .filter(Task.id == task_id, LifeContext.user_id == current_user.id)\
                .first()

    if not task:
        raise HTTPException(status_code=404, detail="Tarea no encontrada o no tiene permiso para acceder a ella")
    return task


"""
Eliminamos una tarea específica por su ID, verificando que pertenece al usuario actual.
Si la tarea no existe o no pertenece al usuario, se devuelve un error 404.
"""
@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)):

    task = db.query(Task)\
        .join(LifeContext)\
            .filter(Task.id == task_id, LifeContext.user_id == current_user.id)\
            .first()
    if not task:
        raise HTTPException(status_code=404, detail="Tarea no encontrada o no tiene acceso")
    
    db.delete(task)
    db.commit()
    return {"detail": "Tarea eliminada exitosamente"}