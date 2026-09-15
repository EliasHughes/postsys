from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.deps import client_ip, get_current_user
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
)
from app.models.user import RefreshToken, User
from app.schemas.common import TokenPair
from app.services.audit import log_action

router = APIRouter(prefix="/auth", tags=["auth"])


def _issue(db: Session, user: User) -> TokenPair:
    access = create_access_token(str(user.id))
    refresh = create_refresh_token(str(user.id))
    db.add(
        RefreshToken(
            user_id=user.id,
            token=refresh,
            expires_at=datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        )
    )
    user.last_login_at = datetime.utcnow()
    db.commit()
    return TokenPair(access_token=access, refresh_token=refresh)


@router.post("/login", response_model=TokenPair)
def login(
    request: Request,
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = db.scalar(select(User).where(User.username == form.username))
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    if not user.is_active:
        raise HTTPException(status_code=401, detail="Usuario inactivo")
    log_action(
        db,
        user_id=user.id,
        company_id=user.company_id,
        branch_id=user.branch_id,
        ip=client_ip(request),
        module="auth",
        action="login",
        entity="User",
        entity_id=str(user.id),
        message="Inicio de sesión",
    )
    return _issue(db, user)


@router.post("/refresh", response_model=TokenPair)
def refresh(payload: dict, db: Session = Depends(get_db)):
    token = payload.get("refresh_token")
    data = decode_token(token or "")
    if not data or data.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Refresh inválido")
    stored = db.scalar(select(RefreshToken).where(RefreshToken.token == token, RefreshToken.revoked.is_(False)))
    if not stored:
        raise HTTPException(status_code=401, detail="Refresh revocado")
    user = db.get(User, int(data["sub"]))
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Usuario inválido")
    stored.revoked = True
    return _issue(db, user)


@router.get("/me")
def me(user: User = Depends(get_current_user)):
    return {
        "id": user.id,
        "username": user.username,
        "full_name": user.full_name,
        "email": user.email,
        "company_id": user.company_id,
        "branch_id": user.branch_id,
        "roles": [r.name for r in user.roles],
        "permissions": sorted(user.permission_codes()),
    }
