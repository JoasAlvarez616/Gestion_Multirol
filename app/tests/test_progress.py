import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.database import Base
from app.models.user import User
from app.models.role import Role
from app.models.task import Task, TaskStatus
from app.models.subtask import SubTask
from app.utils import get_task_progress, get_role_progress


# ---------- FIXTURE DE BASE DE DATOS EN MEMORIA ----------

@pytest.fixture
def session():
    # Base de datos SQLite en memoria (NO usa la real)
    engine = create_engine("sqlite:///:memory:")
    TestingSessionLocal = sessionmaker(bind=engine)

    # Crear todas las tablas
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    yield db

    db.close()


# ---------- TEST PRINCIPAL ----------

def test_progress(session):
    """Test completo de usuarios, roles, tasks y subtasks"""

    # Crear usuarios
    user1 = User(username="Joas", email="joas@example.com", password="1234")
    user2 = User(username="Ana", email="ana@example.com", password="5678")
    session.add_all([user1, user2])
    session.commit()

    # Crear roles
    role1 = Role(name="Estudiante", description="Rol de prueba", user=user1)
    role2 = Role(name="Profesor", description="Rol de prueba", user=user2)
    session.add_all([role1, role2])
    session.commit()

    # Crear tasks
    task1 = Task(
        title="Aprender Python",
        description="Task de prueba",
        role=role1,
        status=TaskStatus.in_progress
    )

    task2 = Task(
        title="Enseñar Matemáticas",
        description="Task de prueba",
        role=role2
    )

    session.add_all([task1, task2])
    session.commit()

    # Crear subtasks
    st1 = SubTask(title="Leer documentación", task=task1, is_completed=True)
    st2 = SubTask(title="Practicar ejercicios", task=task1, is_completed=False)
    st3 = SubTask(title="Preparar clases", task=task2, is_completed=False)

    session.add_all([st1, st2, st3])
    session.commit()

    # -------- VALIDACIONES --------

    # Relaciones
    assert user1.roles[0] == role1
    assert user2.roles[0] == role2

    assert role1.tasks[0] == task1
    assert role2.tasks[0] == task2

    assert task1.subtasks[0] == st1
    assert task1.subtasks[1] == st2
    assert task2.subtasks[0] == st3

    # Progreso
    assert get_task_progress(task1) == 50.0
    assert get_task_progress(task2) == 0.0
    assert get_role_progress(role1) == 50.0
    assert get_role_progress(role2) == 0.0