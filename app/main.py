from fastapi import FastAPI, Depends, HTTPException, status
from app.security.security import create_access_token, verify_password
from sqlalchemy.orm import Session
from app.database.database import SessionLocal, get_db
from app.models.user import User
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
def login(data:Login, db: Session = Depends(get_db)):
    # Aquí validas usuario y contraseña (temporal hardcode)
   user = db.query(User).filter(User.username == data.username).first()
   if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nombre o contraseña incorrectos"
        )
   
   if not verify_password(data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nombre o contraseña incorrectos"
        )
   
   token = create_access_token({"sub": user.username})
   return {"access_token": token, "token_type": "bearer"}

@app.get("/users/")
def read_users(payload: dict = Depends(verify_password)):
    """
    Endpoint protegido: solo accesible con un token válido.
    """
    return {"msg": "Token válido!", "user": payload["sub"]}

# ==============================
# Routers
# ==============================
app.include_router(user.router)
app.include_router(auth.router)

# ==============================
# Crear dependenciancia para la base de datos
# ==============================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()