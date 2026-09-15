from fastapi import APIRouter, Depends
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, require_permission
from app.models.sale import Sale
from app.models.user import User
from sqlalchemy import select

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/sales.csv", dependencies=[Depends(require_permission("reports.export"))])
def sales_csv(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = db.scalars(select(Sale).where(Sale.company_id == user.company_id)).all()
    lines = ["numero,fecha,estado,subtotal,itbis,total"]
    for s in rows:
        lines.append(
            f"{s.number},{s.sold_at},{s.status},{s.subtotal},{s.tax_total},{s.total}"
        )
    return PlainTextResponse("\n".join(lines), media_type="text/csv")
