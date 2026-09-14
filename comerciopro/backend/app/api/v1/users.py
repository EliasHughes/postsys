from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, require_permission
from app.core.security import hash_password
from app.models.user import Role, User, UserRole
from app.models.audit import AuditLog
from app.models.user import User as UserModel

router = APIRouter(tags=["admin"])


class UserIn(BaseModel):
    username: str
    full_name: str
    password: str
    role_slug: str = "cashier"
    email: str | None = None


@router.get("/users", dependencies=[Depends(require_permission("users.edit"))])
def list_users(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = db.scalars(select(User).where(User.company_id == user.company_id)).all()
    return [
        {
            "id": u.id,
            "username": u.username,
            "full_name": u.full_name,
            "is_active": u.is_active,
            "roles": [r.name for r in u.roles],
        }
        for u in rows
    ]


@router.post("/users", dependencies=[Depends(require_permission("users.create"))])
def create_user(payload: UserIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if db.scalar(select(User).where(User.username == payload.username)):
        raise HTTPException(400, "Usuario ya existe")
    role = db.scalar(select(Role).where(Role.slug == payload.role_slug))
    if not role:
        raise HTTPException(400, "Rol inválido")
    u = User(
        company_id=user.company_id,
        branch_id=user.branch_id,
        username=payload.username,
        full_name=payload.full_name,
        email=payload.email,
        hashed_password=hash_password(payload.password),
    )
    db.add(u)
    db.flush()
    db.add(UserRole(user_id=u.id, role_id=role.id))
    db.commit()
    return {"id": u.id}


@router.get("/audit")
def audit(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = db.scalars(
        select(AuditLog).where(AuditLog.company_id == user.company_id).order_by(AuditLog.id.desc()).limit(200)
    ).all()
    return [
        {
            "id": a.id,
            "created_at": a.created_at.isoformat() if a.created_at else None,
            "module": a.module,
            "action": a.action,
            "entity": a.entity,
            "entity_id": a.entity_id,
            "message": a.message,
            "ip": a.ip,
            "result": a.result,
        }
        for a in rows
    ]


@router.get("/roles")
def roles(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = db.scalars(select(Role).where((Role.company_id == user.company_id) | (Role.company_id.is_(None)))).all()
    return [{"id": r.id, "name": r.name, "slug": r.slug} for r in rows]
