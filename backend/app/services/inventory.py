from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.inventory import InventoryBalance, InventoryMovement
from app.models.product import Product


def get_or_create_balance(db: Session, company_id: int, branch_id: int, product_id: int) -> InventoryBalance:
    bal = db.scalar(
        select(InventoryBalance).where(
            InventoryBalance.company_id == company_id,
            InventoryBalance.branch_id == branch_id,
            InventoryBalance.product_id == product_id,
        )
    )
    if not bal:
        product = db.get(Product, product_id)
        bal = InventoryBalance(
            company_id=company_id,
            branch_id=branch_id,
            product_id=product_id,
            qty_on_hand=0,
            qty_reserved=0,
            avg_cost=float(product.cost) if product else 0,
        )
        db.add(bal)
        db.flush()
    return bal


def apply_movement(
    db: Session,
    *,
    company_id: int,
    branch_id: int,
    product_id: int,
    user_id: int | None,
    movement_type: str,
    qty: float,
    cost: float = 0,
    source_doc: str | None = None,
    reason: str | None = None,
    allow_negative: bool = False,
) -> InventoryBalance:
    bal = get_or_create_balance(db, company_id, branch_id, product_id)
    before = float(bal.qty_on_hand)
    after = before + qty
    if after < 0 and not allow_negative:
        raise HTTPException(status_code=400, detail=f"Stock insuficiente para producto {product_id}")
    bal.qty_on_hand = after
    if qty > 0 and cost:
        # promedio ponderado
        if before <= 0:
            bal.avg_cost = cost
        else:
            bal.avg_cost = ((before * float(bal.avg_cost)) + (qty * cost)) / after
    db.add(
        InventoryMovement(
            company_id=company_id,
            branch_id=branch_id,
            product_id=product_id,
            user_id=user_id,
            movement_type=movement_type,
            qty=qty,
            cost=cost,
            qty_before=before,
            qty_after=after,
            source_doc=source_doc,
            reason=reason,
        )
    )
    return bal
