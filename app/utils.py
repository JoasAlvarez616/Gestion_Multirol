# app/utils.py
from app.models.task import Task
from app.models.role import Role

def get_task_progress(task: Task) -> float:
    """
    Calcula el progreso de una Task en porcentaje.
    Si no tiene subtareas, usa el estado de la tarea.
    """
    total_subtasks = len(task.subtasks)
    completed_subtasks = sum(1 for st in task.subtasks if st.is_completed)
    
    if total_subtasks > 0:
        progress = (completed_subtasks / total_subtasks) * 100
    else:
        # Si no tiene subtareas, será 100% si la tarea está completada, sino será 0%
        progress = 100 if task.status.name == "completed" else 0
    
    return progress

def get_role_progress(role: Role) -> float:
    """
    Calcula el progreso global de un Role en porcentaje,
    considerando todas sus tareas y sus subtareas.
    """
    all_task_progress = [get_task_progress(task) for task in role.tasks]
    
    if all_task_progress:
        role_progress = sum(all_task_progress) / len(all_task_progress)
    else:
        role_progress = 0
    
    return role_progress