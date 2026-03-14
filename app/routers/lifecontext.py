from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database.database import get_db
from app.models.lifecontext import LifeContext
from app.models.user import User
from app.schemas.lifecontext import LifeContextCreate, LifeContextResponse
from app.security.dependencies import get_current_user

router = APIRouter(prefix="/lifecontexts",
                    tags=["LifeContexts"]
                    )

@router.post("/", response_model=LifeContextResponse)
def create_context(context: LifeContextCreate, db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_user)):
    new_context = LifeContext(
        name=context.name,
        description=context.description,
        user_id=current_user.id
    )

    db.add(new_context)
    db.commit()
    db.refresh(new_context)
    return new_context

@router.get("/", response_model=List[LifeContextResponse])
def get_my_contexts(db: Session = Depends(get_db), 
                    current_user: User = Depends(get_current_user)):
    return db.query(LifeContext).filter(
        LifeContext.user_id == current_user.id).all()

@router.get("/{context_id}", response_model=LifeContextResponse)
def get_context(context_id: int, db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):
        context = db.query(LifeContext).filter(
        LifeContext.id == context_id,
        LifeContext.user_id == current_user.id
    ).first()
        
        if not context:
             raise HTTPException(status_code=404, detail="Contexto no encontrado")
        
        return context