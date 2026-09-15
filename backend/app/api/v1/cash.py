from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, require_permission
from app.models.cash import CashRegister, CashSession
from app.models.user import User
from app.services.cash import close_session, open_session

router = APIRouter(prefix="/cash", tags=["cash"])


class OpenIn(BaseModel):
    register_id: int
    opening_float: float = 0


class CloseIn(BaseModel):
    session_id: int
    counted_cash: float


@router.get("/registers")
def registers(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = db.scalars(select(CashRegister).where(CashRegister.company_id == user.company_id)).all()
    return [{"id": r.id, "name": r.name, "code": r.code, "branch_id": r.branch_id} for r in rows]


@router.get("/sessions/current")
def current(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    s = db.scalar(
        select(CashSession).where(CashSession.user_id == user.id, CashSession.status == "OPEN")
    )
    if not s:
        return None
    return {
        "id": s.id,
        "status": s.status,
        "opening_float": float(s.opening_float),
        "opened_at": s.opened_at.isoformat() if s.opened_at else None,
        "register_id": s.register_id,
    }


@router.post("/open", dependencies=[Depends(require_permission("cash.open"))])
def open_cash(payload: OpenIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    s = open_session(db, user, payload.register_id, payload.opening_float)
    return {"id": s.id, "status": s.status, "opening_float": float(s.opening_float)}


@router.post("/close", dependencies=[Depends(require_permission("cash.close"))])
def close_cash(payload: CloseIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    s = close_session(db, user, payload.session_id, payload.counted_cash)
    return {
        "id": s.id,
        "status": s.status,
        "expected_cash": float(s.expected_cash),
        "counted_cash": float(s.counted_cash or 0),
        "difference": float(s.difference),
    }
