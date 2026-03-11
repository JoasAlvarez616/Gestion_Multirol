from app.database.database import SessionLocal
from app.models.user import User
from app.models.role import Role
from app.models.task import Task, TaskStatus
from app.models.subtask import SubTask
from app.utils import get_task_progress, get_role_progress

session = SessionLocal()

# Limpiamos datos anteriores para pruebas
session.query(SubTask).delete()
session.query(Task).delete()
session.query(Role).delete()
session.query(User).delete()
session.commit()

print("Creando datos de prueba...")

# Crear usuarios
users = [
    User(username="Joas", email="joas@example.com", password="1234"),
    User(username="Ana", email="ana@example.com", password="5678")
]
session.add_all(users)
session.commit()

# Crear roles
roles = [
    Role(name="Estudiante", description="Rol de prueba", user_id=users[0].id),
    Role(name="Profesor", description="Rol de prueba", user_id=users[1].id)
]
session.add_all(roles)
session.commit()

# Crear tasks y subtasks
tasks = [
    Task(title="Aprender Python", description="Task de prueba", role_id=roles[0].id, status=TaskStatus.in_progress),
    Task(title="Enseñar Matemáticas", description="Task de prueba", role_id=roles[1].id)
]
session.add_all(tasks)
session.commit()

subtasks = [
    SubTask(title="Leer documentación", task_id=tasks[0].id, is_completed=True),
    SubTask(title="Practicar ejercicios", task_id=tasks[0].id, is_completed=False),
    SubTask(title="Preparar clases", task_id=tasks[1].id, is_completed=False)
]
session.add_all(subtasks)
session.commit()

print("Datos de prueba creados.\n")

# Mostrar progreso por usuario, rol y task
for u in session.query(User).all():
    print(f"Usuario: {u.username}")
    for r in u.roles:
        print(f"  Rol: {r.name}")
        print(f"    Progreso global del rol: {get_role_progress(r):.2f}%")
        for t in r.tasks:
            print(f"    Task: {t.title}")
            print(f"      Progreso de la task: {get_task_progress(t):.2f}%")
            for st in t.subtasks:
                print(f"        SubTask: {st.title} - Completada: {st.is_completed}")

session.close()
print("\n Validación completa.")
