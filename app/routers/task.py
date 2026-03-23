from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy import func, and_, or_
from datetime import datetime, date, time, timezone, timedelta

from app.database.database import get_db
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskResponse, TaskUpdateStatus, TaskUpdate, TaskStatus, TaskPriority, TodayDashboardResponse, DashboardSummaryResponse
from app.models.user import User
from app.models.lifecontext import LifeContext
from app.security.dependencies import get_current_user

def user_has_access_condition(current_user: User):
    return or_(
        LifeContext.owner_id == current_user.id,
        LifeContext.members.any(User.id == current_user.id)
    )

router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
)


@router.post("/", response_model=TaskResponse)
def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)):

    # Verificamos que el contexto al que se asigna la tarea pertenece al usuario actual
    context = db.query(LifeContext).filter(
        LifeContext.id == task.context_id,
        user_has_access_condition(current_user)
        ).first()

    if not context:
        raise HTTPException(status_code=400,
                            detail="El contexto no existe o no pertenece al usuario")

    #Calcular siguiente numero dentro del contexto
    max_number = db.query(func.max(Task.context_task_number))\
        .filter(Task.context_id == task.context_id)\
            .scalar()

    next_number = 1 if max_number is None else max_number + 1


    due_date= task.due_date
    if due_date is not None:
        #Si la hora es exactamente 00:00:00,
        #la ajustamos a 23:59 del mismo día para que se muestre en el dashboard de tareas de hoy
        if(
            due_date.hour==0
            and due_date.minute==0
            and due_date.second==0
        ):
            due_date = due_date.replace(hour=23, minute=59)

    # Creamos la tarea
    db_task = Task(
        title=task.title,
        status=TaskStatus.pending,
        priority=task.priority,
        due_date=due_date,
        context_id=task.context_id,
        context_task_number=next_number
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
        user_has_access_condition(current_user))

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
Dashboard de tareas para el día actual,
mostrando solo las tareas que no están completadas y que tienen fecha de vencimiento hoy o en el pasado.
Las tareas se ordenan por fecha de vencimiento (las más próximas primero) y luego por prioridad.
"""
@router.get("/today", response_model=TodayDashboardResponse)
def get_today_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)):

    now = datetime.now(timezone.utc)

    # Calculamos el inicio y fin del día actual
    stat_of_day = datetime(
        year=now.year, 
        month=now.month, 
        day=now.day, 
        hour=0, 
        minute=0, 
        second=0, 
        tzinfo=timezone.utc
        )

    end_of_day = datetime(
        year=now.year,
        month=now.month,
        day=now.day,
        hour=23,
        minute=59,
        second=59,
        tzinfo=timezone.utc
        )

    base_query = db.query(Task)\
    .join(LifeContext)\
    .filter(
        user_has_access_condition(current_user),
        Task.status != TaskStatus.completed,
        Task.due_date != None
    )

    overdue_tasks = base_query\
    .filter(Task.due_date < stat_of_day)\
        .order_by(Task.due_date.asc(),
                  Task.priority.desc())\
                    .all()

    today_tasks = base_query\
    .filter(Task.due_date >= stat_of_day,
            Task.due_date <= end_of_day)\
                .order_by(Task.due_date.asc(),
                            Task.priority.desc())\
                            .all()

    return {
        "overdue": overdue_tasks,
        "today": today_tasks
    }


"""
Dashboard de tareas próximas, mostrando solo las tareas que no están completadas
y que tienen fecha de vencimiento en los próximos 7 días.
"""
@router.get("/upcoming", response_model=List[TaskResponse])
def get_upcoming_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)):

    now = datetime.now(timezone.utc)

    #Inicio de mañana
    start_of_tomorrow = datetime(
        year=now.year,
        month=now.month,
        day=now.day,
        hour=0,
        minute=0,
        second=0,
        tzinfo=timezone.utc
    ) + timedelta(days=1)

    #Fin del día dentro de 7 días
    end_of_range = start_of_tomorrow + timedelta(days=7)
    
    tasks = db.query(Task)\
    .join(LifeContext)\
    .filter(
        user_has_access_condition(current_user),
        Task.status != TaskStatus.completed,
        Task.due_date != None,
        Task.due_date >= start_of_tomorrow,
        Task.due_date <= end_of_range
    )\
    .order_by(Task.due_date.asc(),
              Task.priority.desc())\
    .all()

    return tasks


"""
Dashboard resumen de tareas, mostrando el número de tareas vencidas,
vencen hoy, próximas a vencer,
total pendientes y completadas hoy.
"""
@router.get("/dashboard/summary",
            response_model=DashboardSummaryResponse)
def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    now = datetime.now(timezone.utc)

    start_of_day = datetime(
        year=now.year,
        month=now.month,
        day=now.day,
        hour=0,
        minute=0,
        second=0,
        tzinfo=timezone.utc
    )

    end_of_day = datetime(
        year=now.year,
        month=now.month,
        day=now.day,
        hour=23,
        minute=59,
        second=59,
        tzinfo=timezone.utc
    )

    start_of_tomorrow = start_of_day + timedelta(days=1)
    end_of_upcoming= start_of_tomorrow + timedelta(days=7)

    base_query = db.query(Task).join(LifeContext).filter(
        user_has_access_condition(current_user))


    overdue = base_query.filter(
        Task.status != TaskStatus.completed,
        Task.due_date != None,
        Task.due_date < start_of_day
    ).count()

    today = base_query.filter(
        Task.status != TaskStatus.completed,
        Task.due_date != None,
        Task.due_date >= start_of_day,
        Task.due_date <= end_of_day
    ).count()

    upcoming = base_query.filter(
        Task.status != TaskStatus.completed,
        Task.due_date != None,
        Task.due_date >= start_of_tomorrow,
        Task.due_date <= end_of_upcoming
    ).count()

    total_pending = base_query.filter(
        Task.status != TaskStatus.completed
    ).count()

    completed_today = base_query.filter(
        Task.status == TaskStatus.completed,
        Task.created_at >= start_of_day,
        Task.created_at <= end_of_day
    ).count()

    return {
        "overdue": overdue,
        "today": today,
        "upcoming": upcoming,
        "total_pending": total_pending,
        "completed_today": completed_today
    }

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
            .filter(Task.id == task_id, user_has_access_condition(current_user))\
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
            .filter(Task.id == task_id, user_has_access_condition(current_user))\
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
        user_has_access_condition(current_user))\
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
        user_has_access_condition(current_user))\
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
        due_date = task_update.due_date

        #Si la hora es exactamente 00:00:00,
        #la ajustamos a 23:59 del mismo día para que se muestre en el dashboard de tareas de hoy
        if(
            due_date.hour==0
            and due_date.minute==0
            and due_date.second==0
        ):
            due_date = due_date.replace(hour=23, minute=59)
            task.due_date = due_date

    db.commit()
    db.refresh(task)

    return task