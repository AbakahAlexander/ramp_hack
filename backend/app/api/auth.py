from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.auth import authenticate_user, create_access_token, get_current_user
from app.database import get_db
from app.models.user import StaffUser
from app.schemas import LoginRequest, StaffUserOut, Token

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=Token, summary="Staff login (OAuth2 form — Swagger Authorize)")
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(get_db)],
):
    """Username = staff email. Use this endpoint with Swagger's Authorize button."""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    return Token(access_token=create_access_token(user.id))


@router.post("/login/json", response_model=Token, summary="Staff login (JSON body)")
def login_json(body: LoginRequest, db: Annotated[Session, Depends(get_db)]):
    user = authenticate_user(db, body.email, body.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    return Token(access_token=create_access_token(user.id))


@router.get("/me", response_model=StaffUserOut)
def me(user: Annotated[StaffUser, Depends(get_current_user)]):
    return user
