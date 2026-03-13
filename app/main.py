from fastapi import FastAPI, Depends, HTTPException, status
from app.security.security import create_access_token, verify_token
from pydantic import BaseModel

from app.routers import user, auth
from app.database.database import engine, Base


# ==============================
# Inicializar FastAPI
# ==============================
app = FastAPI(
    title="Sistema de Gestion Multirol",
    version="0.1.0",
    description=(
        "Una aplicación para gestionar múltiples roles y tareas de usuario de un sistema. "
        "Permite a los usuarios crear, editar y eliminar tareas. "
        "También incluye un sistema de notificaciones para mantener a los usuarios informados sobre las tareas asignadas y su progreso."
    ),
)

# Crear tablas si no existen
Base.metadata.create_all(bind=engine)

# ==============================
# Schemas
# ==============================

class Login(BaseModel):
    username: str
    password: str


# ==============================
# Endpoints
# ==============================

@app.get("/")
def root():
    return {"message": "Bienvenido al Sistema de Gestion Multirol"}

@app.post("/login/")
def login(data:Login):
    # Aquí validas usuario y contraseña (temporal hardcode)
    if data.username != "joas" or data.password != "1234":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nombre o contraseña incorrectos"
        )

    token= create_access_token({"sub": data.username})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/users/")
def read_users(payload: dict = Depends(verify_token)):
    """
    Endpoint protegido: solo accesible con un token válido.
    """
    return {"msg": "Token válido!", "user": payload["sub"]}

# ==============================
# Routers
# ==============================
app.include_router(user.router)
app.include_router(auth.router)