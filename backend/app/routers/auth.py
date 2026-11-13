from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import Session, select

from ..auth import authenticate_user, create_token
from ..db import get_session
from ..models import User

router = APIRouter(prefix="/api")


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/auth/login")
def login(payload: LoginRequest, session: Session = Depends(get_session)):
    user = authenticate_user(session, payload.username, payload.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return {"token": create_token(user.username, user.role.value), "role": user.role.value, "full_name": user.full_name}
