from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database.database import get_db
from app.models.task import Task
from app.models.lifecontext import LifeContext
from app.models.user import User
from app.schemas.task import TaskCreate, TaskResponse
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
    life_context = db.query(LifeContext).filter(
        LifeContext.id == task.context_id,
        LifeContext.user_id == current_user.id).first()

    if not life_context:
        raise HTTPException(status_code=404, detail="Contexto no encontrado")

    # Crear la tarea
    new_task = Task(
        title=task.title,
        description=task.description,
        priority=task.priority,
        due_date=task.due_date,
        context_id=task.context_id
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

@router.get("/", response_model=List[TaskResponse])
def get_tasks(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)):

    return db.query(Task).join(LifeContext).filter(
        LifeContext.user_id == current_user.id).all()