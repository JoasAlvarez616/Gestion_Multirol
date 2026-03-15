from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database.database import get_db
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskResponse, TaskUpdateStatus,TaskUpdate, TaskStatus, TaskPriority
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
        priority=task.priority,
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
    skip: int = 0,
    limit: int = 10,
    status: Optional[TaskStatus] = None,
    priority: Optional[TaskPriority] = None,
    context_id: Optional[int] = None,
    order_by: Optional[str] = "created_at",
    order: Optional[str] = "asc",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)):

    query = db.query(Task).join(LifeContext).filter(
        LifeContext.user_id == current_user.id)

    if status:
        query = query.filter(Task.status == status)

    if priority:
        query = query.filter(Task.priority == priority)

    if context_id:
        query = query.filter(Task.context_id == context_id)


    # Ordenar por el campo especificado
    allowed_order_fields = {
        "created_at": Task.created_at,
        "due_date": Task.due_date,
        "priority": Task.priority,
        "status": Task.status,
        "title": Task.title}

    if order_by not in allowed_order_fields:
        raise HTTPException(status_code=400, detail="Campo de ordenación no válido")

    order_column = allowed_order_fields[order_by]

    if order == "desc":
        query = query.order_by(order_column.desc())
    else:
        query = query.order_by(order_column.asc())


    # Paginación
    tasks = query.offset(skip).limit(limit).all()

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


"""
Actualizamos el estado de una tarea específica por su ID,
verificando que pertenece al usuario actual.
"""
@router.patch("/{task_id}", response_model=TaskResponse)
def update_task_status(
    task_id: int,
    task_update: TaskUpdateStatus,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)):

    task = db.query(Task)\
        .join(LifeContext)\
        .filter(
        Task.id == task_id,
        LifeContext.user_id == current_user.id)\
        .first()

    if not task:
        raise HTTPException(status_code=404, detail="Tarea no encontrada o no tiene permiso")

# Actualizamos el estado de la tarea
    task.status = task_update.status
    db.commit()
    db.refresh(task)
    return task


"""
Actualizamos los campos de una tarea específica por su ID,
verificando que pertenece al usuario actual.
"""
@router.patch("/{task_id}/edit", response_model=TaskResponse)
def update_task(
    task_id: int,
    task_update: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)):

    task = db.query(Task)\
        .join(LifeContext)\
        .filter(
        Task.id == task_id,
        LifeContext.user_id == current_user.id)\
        .first()

    if not task:
        raise HTTPException(status_code=404, 
                            detail="Tarea no encontrada o no tiene permiso")

    # Actualizamos solo los campos que se proporcionan
    if task_update.title is not None:
        task.title = task_update.title

    if task_update.description is not None:
        task.description = task_update.description

    if task_update.priority is not None:
        task.priority = task_update.priority

    if task_update.due_date is not None:
        task.due_date = task_update.due_date

    db.commit()
    db.refresh(task)

    return task