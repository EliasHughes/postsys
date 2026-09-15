from datetime import datetime
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.cash import CashMovement, CashRegister, CashSession
from app.models.user import User
from app.services.audit import log_action


def open_session(db: Session, user: User, register_id: int, opening_float: float) -> CashSession:
    existing = db.scalar(
        select(CashSession).where(
            CashSession.register_id == register_id,
            CashSession.status == "OPEN",
        )
    )
    if existing:
        raise HTTPException(status_code=400, detail="Ya existe una sesión abierta en esta caja")
    register = db.get(CashRegister, register_id)
    if not register:
        raise HTTPException(status_code=404, detail="Caja no encontrada")
    session = CashSession(
        company_id=user.company_id,
        branch_id=register.branch_id,
        register_id=register.id,
        user_id=user.id,
        opening_float=opening_float,
        status="OPEN",
    )
    db.add(session)
    db.flush()
    db.add(
        CashMovement(
            session_id=session.id,
            company_id=user.company_id,
            user_id=user.id,
            kind="IN",
            method="CASH",
            amount=opening_float,
            notes="Fondo inicial",
        )
    )
    log_action(
        db,
        user_id=user.id,
        company_id=user.company_id,
        branch_id=register.branch_id,
        module="cash",
        action="open",
        entity="CashSession",
        entity_id=str(session.id),
        new_value=str(opening_float),
    )
    db.commit()
    db.refresh(session)
    return session


def close_session(db: Session, user: User, session_id: int, counted_cash: float) -> CashSession:
    session = db.get(CashSession, session_id)
    if not session or session.status != "OPEN":
        raise HTTPException(status_code=400, detail="Sesión no abierta")

    cash_in = sum(float(m.amount) for m in session.movements if m.kind in {"SALE_CASH", "IN", "DEPOSIT"})
    cash_out = sum(float(m.amount) for m in session.movements if m.kind in {"REFUND", "EXPENSE", "WITHDRAW"})
    expected = float(session.opening_float) + cash_in - cash_out - float(session.opening_float)
    # opening_float already included as IN movement; avoid double count:
    expected = cash_in - cash_out
    session.expected_cash = round(expected, 2)
    session.counted_cash = counted_cash
    session.difference = round(counted_cash - expected, 2)
    session.status = "CLOSED"
    session.closed_at = datetime.utcnow()
    log_action(
        db,
        user_id=user.id,
        company_id=user.company_id,
        branch_id=session.branch_id,
        module="cash",
        action="close",
        entity="CashSession",
        entity_id=str(session.id),
        new_value=f"counted={counted_cash};expected={expected};diff={session.difference}",
    )
    db.commit()
    db.refresh(session)
    return session
