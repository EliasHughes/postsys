from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.party import Customer, Supplier
from app.models.user import User

router = APIRouter(tags=["parties"])


class CustomerIn(BaseModel):
    name: str
    document_type: str = "CEDULA"
    document: str | None = None
    phone: str | None = None
    email: str | None = None
    credit_limit: float = 0


class SupplierIn(BaseModel):
    name: str
    rnc: str | None = None
    phone: str | None = None
    email: str | None = None


@router.get("/customers")
def list_customers(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = db.scalars(select(Customer).where(Customer.company_id == user.company_id)).all()
    return [
        {
            "id": c.id,
            "name": c.name,
            "document": c.document,
            "phone": c.phone,
            "credit_limit": float(c.credit_limit),
            "balance": float(c.balance),
            "loyalty_points": c.loyalty_points,
            "is_final_consumer": c.is_final_consumer,
        }
        for c in rows
    ]


@router.post("/customers")
def create_customer(payload: CustomerIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    c = Customer(company_id=user.company_id, **payload.model_dump())
    db.add(c)
    db.commit()
    db.refresh(c)
    return {"id": c.id, "name": c.name}


@router.get("/suppliers")
def list_suppliers(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = db.scalars(select(Supplier).where(Supplier.company_id == user.company_id)).all()
    return [
        {"id": s.id, "name": s.name, "rnc": s.rnc, "phone": s.phone, "balance": float(s.balance)}
        for s in rows
    ]


@router.post("/suppliers")
def create_supplier(payload: SupplierIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    s = Supplier(company_id=user.company_id, **payload.model_dump())
    db.add(s)
    db.commit()
    db.refresh(s)
    return {"id": s.id, "name": s.name}
