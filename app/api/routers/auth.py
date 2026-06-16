from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from app.schemas import LoginIn, Token, ChangePasswordIn, UserInDB
from app.db.session import get_db
from app import models
from app.utils.security import verify_password, create_access_token, get_password_hash
from app.api.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=Token)
def login(data: LoginIn, response: Response, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == data.email).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials or inactive account")
    if not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_access_token({"sub": str(user.id)})
    response.set_cookie(key="access_token", value=token, httponly=True)
    return {"access_token": token}


@router.post("/change-password", response_model=dict)
def change_password(payload: ChangePasswordIn, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    # If user must change password, allow change without old password
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    if not current_user.must_change_password and payload.old_password:
        if not verify_password(payload.old_password, current_user.hashed_password):
            raise HTTPException(status_code=400, detail="Old password incorrect")

    current_user.hashed_password = get_password_hash(payload.new_password)
    current_user.must_change_password = False
    db.add(current_user)
    db.commit()
    return {"detail": "password_changed"}


@router.get("/me", response_model=UserInDB)
def me(current_user: models.User = Depends(get_current_user)):
    return current_user
