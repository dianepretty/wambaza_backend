from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas import UserCreate, UserUpdate, UserOut
from app.db.session import get_db
from app import models
from app.utils.security import get_password_hash
from app.utils.emailer import send_temporary_password
from app.api.deps import require_admin
import secrets

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserOut, dependencies=[Depends(require_admin)])
def create_publisher(payload: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")
    temp_password = secrets.token_urlsafe(8)
    user = models.User(
        name=payload.name,
        email=payload.email,
        role="publisher",
        hashed_password=get_password_hash(temp_password),
        must_change_password=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    try:
        send_temporary_password(user.email, temp_password)
    except Exception:
        # don't fail creation if email fails
        pass
    return user


@router.get("", response_model=list[UserOut], dependencies=[Depends(require_admin)])
def list_users(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    return users


@router.patch("/{id}", response_model=UserOut, dependencies=[Depends(require_admin)])
def update_user(id: int, payload: UserUpdate, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if payload.name is not None:
        user.name = payload.name
    if payload.email is not None:
        user.email = payload.email
    db.commit()
    db.refresh(user)
    return user


@router.patch("/{id}/deactivate", dependencies=[Depends(require_admin)])
def deactivate_user(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = False
    db.commit()
    return {"detail": "deactivated"}


@router.patch("/{id}/activate", dependencies=[Depends(require_admin)])
def activate_user(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = True
    db.commit()
    return {"detail": "activated"}
