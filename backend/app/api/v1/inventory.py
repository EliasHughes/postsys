from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, require_permission
from app.models.inventory import InventoryBalance, InventoryMovement
from app.models.product import Product
from app.models.user import User
from app.services.inventory import apply_movement

router = APIRouter(prefix="/inventory", tags=["inventory"])


class AdjustIn(BaseModel):
    product_id: int
    qty: float
    reason: str
    movement_type: str = "ADJUST"  # ADJUST, IN, OUT, LOSS


@router.get("")
def balances(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = db.scalars(
        select(InventoryBalance).where(
            InventoryBalance.company_id == user.company_id,
            InventoryBalance.branch_id == user.branch_id,
        )
    ).all()
    out = []
    for b in rows:
        p = db.get(Product, b.product_id)
        out.append(
            {
                "product_id": b.product_id,
                "name": p.name if p else "",
                "sku": p.sku if p else "",
                "qty_on_hand": float(b.qty_on_hand),
                "qty_reserved": float(b.qty_reserved),
                "qty_available": b.qty_available,
                "avg_cost": float(b.avg_cost),
                "value": float(b.qty_on_hand) * float(b.avg_cost),
                "min_stock": float(p.min_stock) if p else 0,
            }
        )
    return out


@router.get("/kardex/{product_id}")
def kardex(product_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = db.scalars(
        select(InventoryMovement)
        .where(
            InventoryMovement.company_id == user.company_id,
            InventoryMovement.product_id == product_id,
        )
        .order_by(InventoryMovement.id.desc())
        .limit(200)
    ).all()
    return [
        {
            "id": m.id,
            "moved_at": m.moved_at.isoformat() if m.moved_at else None,
            "type": m.movement_type,
            "qty": float(m.qty),
            "cost": float(m.cost),
            "qty_before": float(m.qty_before),
            "qty_after": float(m.qty_after),
            "source_doc": m.source_doc,
            "reason": m.reason,
        }
        for m in rows
    ]


@router.post("/adjust", dependencies=[Depends(require_permission("inventory.adjust"))])
def adjust(payload: AdjustIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    apply_movement(
        db,
        company_id=user.company_id,
        branch_id=user.branch_id,
        product_id=payload.product_id,
        user_id=user.id,
        movement_type=payload.movement_type,
        qty=payload.qty,
        source_doc="ADJ",
        reason=payload.reason,
        allow_negative=False,
    )
    db.commit()
    return {"ok": True}
