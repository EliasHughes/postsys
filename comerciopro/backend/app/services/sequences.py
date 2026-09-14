from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.sale import Sale, Quote, ReturnDoc
from app.models.purchase import Purchase
from app.models.accounting import JournalEntry


def next_number(db: Session, model, prefix: str, company_id: int) -> str:
    count = db.scalar(select(func.count()).select_from(model).where(model.company_id == company_id)) or 0
    return f"{prefix}-{count + 1:06d}"


def next_sale_number(db: Session, company_id: int) -> str:
    return next_number(db, Sale, "FAC", company_id)


def next_quote_number(db: Session, company_id: int) -> str:
    return next_number(db, Quote, "COT", company_id)


def next_return_number(db: Session, company_id: int) -> str:
    return next_number(db, ReturnDoc, "NC", company_id)


def next_purchase_number(db: Session, company_id: int) -> str:
    return next_number(db, Purchase, "OC", company_id)


def next_journal_number(db: Session, company_id: int) -> str:
    return next_number(db, JournalEntry, "AS", company_id)
