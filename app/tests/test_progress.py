from app.database.database import SessionLocal
from app.models.user import User
from app.models.role import Role
from app.models.task import Task
from app.models.subtask import SubTask
from app.utils import get_task_progress, get_role_progress

session = SessionLocal()

# Crear datos de prueba si no existen
if not session.query(User).first():
    print("Creando datos de prueba...")
    u = User(username="Joas", email="joas@example.com", password="1234")
    session.add(u)
    session.commit()

    r = Role(name="Estudiante", description="Rol de prueba", user_id=u.id)
    session.add(r)
    session.commit()

    t = Task(title="Aprender Python", description="Tarea de prueba", role_id=r.id)
    session.add(t)
    session.commit()

    st1 = SubTask(title="Leer documentación", task_id=t.id, is_completed=True)
    st2 = SubTask(title="Practicar ejercicios", task_id=t.id, is_completed=False)
    session.add_all([st1, st2])
    session.commit()
    print("Datos de prueba creados.")

# Obtener Task y Role
task = session.query(Task).first()
role = session.query(Role).first()

# Mostrar progreso
if task:
    print(f"Tarea '{task.title}' progreso: {get_task_progress(task):.2f}%")
if role:
    print(f"Rol '{role.name}' progreso global: {get_role_progress(role):.2f}%")

session.close()