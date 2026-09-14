from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.audit import AuditLog
from app.models.cash import CashSession
from app.models.inventory import InventoryBalance
from app.models.party import Customer, Supplier
from app.models.product import Product
from app.models.sale import Sale, SaleDetail
from app.models.user import User
from app.models.accounting import AccountReceivable, AccountPayable

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("")
def dashboard(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    now = datetime.utcnow()
    start_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    start_week = start_day - timedelta(days=start_day.weekday())
    start_month = start_day.replace(day=1)
    start_year = start_day.replace(month=1, day=1)

    def sum_sales(since):
        val = db.scalar(
            select(func.coalesce(func.sum(Sale.total), 0)).where(
                Sale.company_id == user.company_id,
                Sale.status.in_(["PAID", "INVOICED", "CONFIRMED"]),
                Sale.sold_at >= since,
            )
        )
        return float(val or 0)

    def count_sales(since):
        return db.scalar(
            select(func.count()).select_from(Sale).where(
                Sale.company_id == user.company_id, Sale.sold_at >= since
            )
        ) or 0

    today = sum_sales(start_day)
    today_n = count_sales(start_day)
    inv_value = float(
        db.scalar(
            select(func.coalesce(func.sum(InventoryBalance.qty_on_hand * InventoryBalance.avg_cost), 0)).where(
                InventoryBalance.company_id == user.company_id
            )
        )
        or 0
    )
    prod_count = db.scalar(select(func.count()).select_from(Product).where(Product.company_id == user.company_id)) or 0
    open_cash = db.scalar(
        select(CashSession).where(CashSession.company_id == user.company_id, CashSession.status == "OPEN")
    )
    ar = float(
        db.scalar(select(func.coalesce(func.sum(AccountReceivable.balance), 0)).where(AccountReceivable.company_id == user.company_id))
        or 0
    )
    ap = float(
        db.scalar(select(func.coalesce(func.sum(AccountPayable.balance), 0)).where(AccountPayable.company_id == user.company_id))
        or 0
    )

    last7 = []
    for i in range(6, -1, -1):
        d0 = start_day - timedelta(days=i)
        d1 = d0 + timedelta(days=1)
        last7.append(
            {
                "date": d0.strftime("%d/%m"),
                "total": float(
                    db.scalar(
                        select(func.coalesce(func.sum(Sale.total), 0)).where(
                            Sale.company_id == user.company_id,
                            Sale.sold_at >= d0,
                            Sale.sold_at < d1,
                        )
                    )
                    or 0
                ),
            }
        )

    top = db.execute(
        select(SaleDetail.description, func.sum(SaleDetail.line_total))
        .join(Sale)
        .where(Sale.company_id == user.company_id)
        .group_by(SaleDetail.description)
        .order_by(func.sum(SaleDetail.line_total).desc())
        .limit(5)
    ).all()

    logs = db.scalars(
        select(AuditLog).where(AuditLog.company_id == user.company_id).order_by(AuditLog.id.desc()).limit(12)
    ).all()

    return {
        "sales_today": today,
        "sales_today_count": today_n,
        "sales_week": sum_sales(start_week),
        "sales_month": sum_sales(start_month),
        "sales_year": sum_sales(start_year),
        "avg_ticket": round(today / today_n, 2) if today_n else 0,
        "inventory_value": inv_value,
        "product_count": prod_count,
        "cash_open": bool(open_cash),
        "customers": db.scalar(select(func.count()).select_from(Customer).where(Customer.company_id == user.company_id)) or 0,
        "suppliers": db.scalar(select(func.count()).select_from(Supplier).where(Supplier.company_id == user.company_id)) or 0,
        "ar": ar,
        "ap": ap,
        "sales_7d": last7,
        "top_products": [{"name": n, "total": float(t)} for n, t in top],
        "audit": [
            {
                "module": l.module,
                "action": l.action,
                "message": l.message,
                "entity_id": l.entity_id,
                "created_at": l.created_at.isoformat() if l.created_at else None,
            }
            for l in logs
        ],
    }
