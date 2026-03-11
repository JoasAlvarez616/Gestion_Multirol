import pytest
from app.database.database import SessionLocal, Base, engine
from app.models.user import User
from app.models.role import Role
from app.models.task import Task, TaskStatus
from app.models.subtask import SubTask
from app.utils import get_task_progress, get_role_progress

@pytest.fixture
def session():
    """Crea una sesión de prueba y las tablas temporales"""
    Base.metadata.create_all(bind=engine)  # Crear tablas
    db = SessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)  # Limpiar tablas

def test_progress(session):
    """Test completo de usuarios, roles, tasks y subtasks"""

    # Crear usuarios
    user1 = User(username="Joas", email="joas@example.com", password="1234")
    user2 = User(username="Ana", email="ana@example.com", password="5678")
    session.add_all([user1, user2])
    session.commit()

    # Crear roles
    role1 = Role(name="Estudiante", description="Rol de prueba", user_id=user1.id)
    role2 = Role(name="Profesor", description="Rol de prueba", user_id=user2.id)
    session.add_all([role1, role2])
    session.commit()

    # Crear tasks
    task1 = Task(title="Aprender Python", description="Task de prueba", role_id=role1.id, status=TaskStatus.in_progress)
    task2 = Task(title="Enseñar Matemáticas", description="Task de prueba", role_id=role2.id)
    session.add_all([task1, task2])
    session.commit()

    # Crear subtasks
    st1 = SubTask(title="Leer documentación", task_id=task1.id, is_completed=True)
    st2 = SubTask(title="Practicar ejercicios", task_id=task1.id, is_completed=False)
    st3 = SubTask(title="Preparar clases", task_id=task2.id, is_completed=False)
    session.add_all([st1, st2, st3])
    session.commit()

    # ---- Validaciones ----

    # Validar usuarios y roles
    assert user1.roles[0] == role1
    assert user2.roles[0] == role2

    # Validar roles y tasks
    assert role1.tasks[0] == task1
    assert role2.tasks[0] == task2

    # Validar tasks y subtasks
    assert task1.subtasks[0] == st1
    assert task1.subtasks[1] == st2
    assert task2.subtasks[0] == st3

    # Validar progreso
    assert get_task_progress(task1) == 50.0      # 1 de 2 subtasks completadas
    assert get_task_progress(task2) == 0.0       # 0 de 1 subtask completada
    assert get_role_progress(role1) == 50.0      # Solo una task con 50%
    assert get_role_progress(role2) == 0.0       # Solo una task con 0%