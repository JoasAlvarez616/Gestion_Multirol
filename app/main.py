from fastapi import FastAPI, Depends, Security, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from datetime import datetime, timedelta
import jwt

from app.routers import user, auth
from app.database.database import engine, Base


# ==============================
# Configuración de JWT
# ==============================
SECRET_KEY = "R2Q7D7Z1"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

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
# Security
# ==============================
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="Login")

# ==============================
# Endpoints
# ==============================
@app.get("/")
def root():
    return {"message": "Bienvenido al Sistema de Gestion Multirol"}

@app.post("/login/")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # Aquí validas usuario y contraseña (temporal hardcode)
    if form_data.username != "joas" or form_data.password != "1234":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nombre o contraseña incorrectos"
        )

    # Generar token
    expires = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": form_data.username, "exp": expires}
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": token, "token_type": "bearer"}

@app.get("/users/")
def read_users(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Token expirado"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Token inválido"
        )
    return {"msg": "Token válido!", "user": payload["sub"]}

# ==============================
# Routers
# ==============================
app.include_router(user.router)
app.include_router(auth.router)