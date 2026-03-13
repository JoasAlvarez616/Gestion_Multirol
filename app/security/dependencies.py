from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.security.jwt import verify_access_token
from app.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
        ):
    payload = verify_access_token(token)

    if payload is None:
        raise HTTPException(status_code=401, detail="Token expirado o inválido")

    username: str = payload.get("sub")

    user = db.query(User).filter(User.username == username).first()

    if user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    return user