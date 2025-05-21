from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.auth import ChangePasswordByTokenRequest, TokenResponse, ChangePasswordRequest
from app.auth import auth as auth_service
from app.auth.dependencies import get_db, get_current_user
from app.models.user import User
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login")
def login(login_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    email = login_data.username
    password = login_data.password
    token = auth_service.login_user(db, email, password)
    return TokenResponse(access_token=token)

@router.post("/change-password")
def change_password(
    password_data: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    auth_service.change_user_password(db, current_user.id, password_data.old_password, password_data.new_password)
    return {"message": "Password updated successfully"}

@router.post("/change-password-with-token/{change_password_token}")
def change_password_with_token(
    change_password_token: str,
    password_data: ChangePasswordByTokenRequest,
    db: Session = Depends(get_db)
):
    result = auth_service.change_user_password_with_token(
        db,
        change_password_token=change_password_token,
        new_password=password_data.new_password,
        retype_new_password=password_data.retype_new_password
    )
    return result
