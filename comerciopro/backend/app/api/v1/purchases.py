from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, require_permission
from app.models.accounting import AccountPayable
from app.models.purchase import Purchase, PurchaseDetail
from app.models.user import User
from app.services.accounting import ACCOUNT_CODES, post_entry
from app.services.inventory import apply_movement
from app.services.sequences import next_purchase_number

router = APIRouter(prefix="/purchases", tags=["purchases"])


class PurchaseLineIn(BaseModel):
    product_id: int
    qty: float = Field(gt=0)
    unit_cost: float
    description: str = ""


class PurchaseIn(BaseModel):
    supplier_id: int
    notes: str | None = None
    items: list[PurchaseLineIn]


@router.get("")
def list_purchases(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = db.scalars(select(Purchase).where(Purchase.company_id == user.company_id).order_by(Purchase.id.desc())).all()
    return [
        {
            "id": p.id,
            "number": p.number,
            "status": p.status,
            "supplier_id": p.supplier_id,
            "total": float(p.total),
            "ordered_at": p.ordered_at.isoformat() if p.ordered_at else None,
        }
        for p in rows
    ]


@router.post("", dependencies=[Depends(require_permission("purchases.create"))])
def create_purchase(payload: PurchaseIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    po = Purchase(
        company_id=user.company_id,
        branch_id=user.branch_id,
        supplier_id=payload.supplier_id,
        user_id=user.id,
        number=next_purchase_number(db, user.company_id),
        status="APPROVED",
        notes=payload.notes,
    )
    db.add(po)
    db.flush()
    subtotal = tax = 0.0
    for line in payload.items:
        net = line.qty * line.unit_cost
        t = round(net * 0.18, 2)
        db.add(
            PurchaseDetail(
                purchase_id=po.id,
                product_id=line.product_id,
                description=line.description,
                qty=line.qty,
                unit_cost=line.unit_cost,
                tax_rate=0.18,
                tax_amount=t,
                line_total=net + t,
            )
        )
        subtotal += net
        tax += t
    po.subtotal = subtotal
    po.tax_total = tax
    po.total = subtotal + tax
    db.commit()
    db.refresh(po)
    return {"id": po.id, "number": po.number, "total": float(po.total)}


@router.post("/{purchase_id}/receive", dependencies=[Depends(require_permission("purchases.receive"))])
def receive(purchase_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    po = db.get(Purchase, purchase_id)
    if not po or po.company_id != user.company_id:
        raise HTTPException(404, "OC no encontrada")
    if po.status in {"RECEIVED", "CANCELLED"}:
        raise HTTPException(400, "OC no receptible")
    for line in po.details:
        apply_movement(
            db,
            company_id=user.company_id,
            branch_id=po.branch_id,
            product_id=line.product_id,
            user_id=user.id,
            movement_type="PURCHASE",
            qty=float(line.qty),
            cost=float(line.unit_cost),
            source_doc=po.number,
            reason="Recepción OC",
        )
        line.qty_received = line.qty
    po.status = "RECEIVED"
    db.add(
        AccountPayable(
            company_id=user.company_id,
            supplier_id=po.supplier_id,
            purchase_id=po.id,
            number=po.number,
            original_amount=float(po.total),
            balance=float(po.total),
        )
    )
    post_entry(
        db,
        company_id=user.company_id,
        branch_id=po.branch_id,
        user_id=user.id,
        source="PURCHASE",
        source_id=po.number,
        concept=f"Compra {po.number}",
        lines=[
            (ACCOUNT_CODES["INVENTORY"], float(po.subtotal), 0, "Mercancía"),
            (ACCOUNT_CODES["ITBIS_PAID"], float(po.tax_total), 0, "ITBIS"),
            (ACCOUNT_CODES["AP"], 0, float(po.total), "CxP"),
        ],
    )
    db.commit()
    return {"ok": True, "status": po.status}
