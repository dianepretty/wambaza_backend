import logging
import secrets
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from app.schemas import LoginIn, Token, ChangePasswordIn, ForgotPasswordIn, ResetPasswordIn, UserInDB, UserUpdate
from app.db.session import get_db
from app import models
from app.utils.security import verify_password, create_access_token, get_password_hash
from app.utils.emailer import send_otp_email
from app.api.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])
logger = logging.getLogger(__name__)

OTP_EXPIRE_MINUTES = 10


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


@router.post("/logout", response_model=dict)
def logout(response: Response):
    response.delete_cookie(key="access_token")
    return {"detail": "logged_out"}


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


@router.patch("/me", response_model=UserInDB)
def update_me(payload: UserUpdate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if payload.name is not None:
        current_user.name = payload.name
    if payload.email is not None:
        current_user.email = payload.email
    db.commit()
    db.refresh(current_user)
    return current_user


@router.post("/forgot-password", response_model=dict)
def forgot_password(payload: ForgotPasswordIn, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == payload.email).first()
    if user and user.is_active:
        otp = f"{secrets.randbelow(1000000):06d}"
        user.reset_otp_hash = get_password_hash(otp)
        user.reset_otp_expires_at = datetime.utcnow() + timedelta(minutes=OTP_EXPIRE_MINUTES)
        db.add(user)
        db.commit()
        try:
            send_otp_email(user.name, user.email, otp)
        except Exception as e:
            logger.error(f"Failed to send OTP email to {user.email}: {e}")
    # Always return a generic response so we don't reveal whether an email is registered
    return {"detail": "If that email exists, a reset code has been sent."}


@router.post("/reset-password", response_model=dict)
def reset_password(payload: ResetPasswordIn, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == payload.email).first()
    if (
        not user
        or not user.reset_otp_hash
        or not user.reset_otp_expires_at
        or user.reset_otp_expires_at < datetime.utcnow()
        or not verify_password(payload.otp, user.reset_otp_hash)
    ):
        raise HTTPException(status_code=400, detail="Invalid or expired reset code")

    user.hashed_password = get_password_hash(payload.new_password)
    user.must_change_password = False
    user.reset_otp_hash = None
    user.reset_otp_expires_at = None
    db.add(user)
    db.commit()
    return {"detail": "password_reset"}
