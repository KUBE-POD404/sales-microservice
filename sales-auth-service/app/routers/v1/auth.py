from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.auth import (
    SignupRequest,
    SignupResponse,
    LoginRequest,
    TokenResponse,
)

from app.services.auth_service import signup, login

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/health")
def health():
    return {"status": "ok"}


@router.post("/signup", response_model=SignupResponse)
def signup_user(payload: SignupRequest, db: Session = Depends(get_db)):

    result = signup(
        db=db,
        org_name=payload.organization_name,
        org_slug=payload.organization_slug,
        email=payload.email,
        password=payload.password,
    )

    return result


@router.post("/login", response_model=TokenResponse)
def login_user(payload: LoginRequest, db: Session = Depends(get_db)):

    token = login(
        db=db,
        org_slug=payload.organization_slug,
        email=payload.email,
        password=payload.password,
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }