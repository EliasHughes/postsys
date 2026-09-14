from fastapi import APIRouter, Depends, Request
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.core.deps import client_ip, get_current_user, require_permission
from app.models.sale import Sale
from app.models.user import User
from app.schemas.sales import SaleCreate
from app.services.sales import create_sale

router = APIRouter(prefix="/sales", tags=["sales"])


def _dump(sale: Sale) -> dict:
    return {
        "id": sale.id,
        "number": sale.number,
        "status": sale.status,
        "sold_at": sale.sold_at.isoformat() if sale.sold_at else None,
        "customer_id": sale.customer_id,
        "subtotal": float(sale.subtotal),
        "discount_global": float(sale.discount_global),
        "tax_total": float(sale.tax_total),
        "total": float(sale.total),
        "paid_total": float(sale.paid_total),
        "change_amount": float(sale.change_amount),
        "items": [
            {
                "product_id": d.product_id,
                "description": d.description,
                "qty": float(d.qty),
                "unit_price": float(d.unit_price),
                "discount": float(d.discount),
                "tax_amount": float(d.tax_amount),
                "line_total": float(d.line_total),
            }
            for d in sale.details
        ],
        "payments": [
            {"method": p.method, "amount": float(p.amount), "reference": p.reference}
            for p in sale.payments
        ],
    }


@router.post("", dependencies=[Depends(require_permission("sales.create"))])
def post_sale(
    payload: SaleCreate,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    sale = create_sale(db, payload, user, ip=client_ip(request))
    sale = db.scalar(
        select(Sale).options(joinedload(Sale.details), joinedload(Sale.payments)).where(Sale.id == sale.id)
    )
    return _dump(sale)


@router.get("")
def list_sales(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = db.scalars(
        select(Sale)
        .options(joinedload(Sale.details), joinedload(Sale.payments))
        .where(Sale.company_id == user.company_id)
        .order_by(Sale.id.desc())
        .limit(200)
    ).unique().all()
    return [_dump(s) for s in rows]


@router.get("/{sale_id}")
def get_sale(sale_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    sale = db.scalar(
        select(Sale).options(joinedload(Sale.details), joinedload(Sale.payments)).where(Sale.id == sale_id)
    )
    return _dump(sale)
