from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from app.database.database import get_db
from app.models import User
from app.security.hashing import verify_password
from app.security.jwt import create_access_token

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):

    user = db.query(User).filter(User.username == form_data.username).first()

    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=401, detail="Nombre o contraseña incorrectos")

    access_token = create_access_token({"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}