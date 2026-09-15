from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.core.deps import get_current_user, require_permission
from app.models.accounting import Account, JournalEntry, JournalEntryLine
from app.models.user import User
from app.services.accounting import post_entry

router = APIRouter(prefix="/accounting", tags=["accounting"])


class ManualIn(BaseModel):
    concept: str
    debit_code: str
    credit_code: str
    amount: float


@router.get("/accounts")
def accounts(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = db.scalars(select(Account).where(Account.company_id == user.company_id).order_by(Account.code)).all()
    balances = {}
    lines = db.execute(
        select(JournalEntryLine.account_id, func.sum(JournalEntryLine.debit), func.sum(JournalEntryLine.credit))
        .join(JournalEntry)
        .where(JournalEntry.company_id == user.company_id)
        .group_by(JournalEntryLine.account_id)
    ).all()
    for acc_id, d, c in lines:
        balances[acc_id] = float(d or 0) - float(c or 0)
    out = []
    for a in rows:
        raw = balances.get(a.id, 0.0)
        # nature credit accounts shown as credit-positive
        shown = raw if a.nature == "DEBIT" else -raw
        out.append(
            {
                "id": a.id,
                "code": a.code,
                "name": a.name,
                "type": a.type,
                "nature": a.nature,
                "balance": round(shown, 2),
            }
        )
    return out


@router.get("/journal")
def journal(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = db.scalars(
        select(JournalEntry)
        .options(joinedload(JournalEntry.lines).joinedload(JournalEntryLine.account))
        .where(JournalEntry.company_id == user.company_id)
        .order_by(JournalEntry.id.desc())
        .limit(100)
    ).unique().all()
    return [
        {
            "id": e.id,
            "number": e.number,
            "source": e.source,
            "concept": e.concept,
            "posted_at": e.posted_at.isoformat() if e.posted_at else None,
            "lines": [
                {
                    "code": ln.account.code if ln.account else "",
                    "name": ln.account.name if ln.account else "",
                    "debit": float(ln.debit),
                    "credit": float(ln.credit),
                }
                for ln in e.lines
            ],
        }
        for e in rows
    ]


@router.post("/manual", dependencies=[Depends(require_permission("accounting.create"))])
def manual(payload: ManualIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if payload.amount <= 0:
        raise HTTPException(400, "Monto inválido")
    post_entry(
        db,
        company_id=user.company_id,
        branch_id=user.branch_id,
        user_id=user.id,
        source="MANUAL",
        source_id="MAN",
        concept=payload.concept,
        lines=[
            (payload.debit_code, payload.amount, 0, payload.concept),
            (payload.credit_code, 0, payload.amount, payload.concept),
        ],
    )
    db.commit()
    return {"ok": True}


@router.get("/trial-balance")
def trial_balance(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    data = accounts(db, user)
    debit = sum(a["balance"] for a in data if a["nature"] == "DEBIT")
    credit = sum(a["balance"] for a in data if a["nature"] == "CREDIT")
    return {"rows": data, "total_debit": round(debit, 2), "total_credit": round(credit, 2)}


@router.get("/income-statement")
def income_statement(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    data = {a["code"]: a["balance"] for a in accounts(db, user)}
    sales = data.get("4101", 0)
    cogs = data.get("5101", 0)
    expenses = data.get("6101", 0)
    gross = sales - cogs
    net = gross - expenses
    return {"sales": sales, "cogs": cogs, "gross_profit": gross, "expenses": expenses, "net_income": net}


@router.get("/balance-sheet")
def balance_sheet(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = accounts(db, user)
    assets = [a for a in rows if a["type"] == "ASSET"]
    liabilities = [a for a in rows if a["type"] == "LIABILITY"]
    equity = [a for a in rows if a["type"] == "EQUITY"]
    return {
        "assets": assets,
        "liabilities": liabilities,
        "equity": equity,
        "total_assets": round(sum(a["balance"] for a in assets), 2),
        "total_liabilities": round(sum(a["balance"] for a in liabilities), 2),
        "total_equity": round(sum(a["balance"] for a in equity), 2),
    }
