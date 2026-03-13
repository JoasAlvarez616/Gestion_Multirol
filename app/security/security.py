from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta
import jwt

# ==============================
# Configuración de JWT
# ==============================

SECRET_KEY = "R2Q7D7Z1"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# ==============================
# OAuth2_scheme
# ==============================

oauth2_scheme= OAuth2PasswordBearer(tokenUrl="/login/")

# ==============================
# Crear Token
# ==============================

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# ==============================
# Verificar Token
# ==============================

def verify_token(token: str = Depends(oauth2_scheme)):
    """
    Funcion reusable para validar token JWT.
    Devuelve el payload si el token es válido, o lanza una excepción si no lo es.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )