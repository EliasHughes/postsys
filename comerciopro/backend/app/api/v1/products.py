from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, require_permission
from app.models.catalog import Category
from app.models.inventory import InventoryBalance
from app.models.product import Product
from app.models.user import User

router = APIRouter(prefix="/products", tags=["products"])


class ProductIn(BaseModel):
    sku: str
    barcode: str | None = None
    name: str
    category_id: int | None = None
    cost: float = 0
    price: float
    wholesale_price: float | None = None
    min_stock: float = 0
    reorder_point: float = 0
    tax_id: int | None = None
    is_active: bool = True


def _serialize(p: Product, qty: float | None = None) -> dict:
    return {
        "id": p.id,
        "sku": p.sku,
        "barcode": p.barcode,
        "name": p.name,
        "category_id": p.category_id,
        "category": p.category.name if p.category else None,
        "cost": float(p.cost),
        "price": float(p.price),
        "wholesale_price": float(p.wholesale_price) if p.wholesale_price is not None else None,
        "min_stock": float(p.min_stock),
        "reorder_point": float(p.reorder_point),
        "expiration_date": str(p.expiration_date) if p.expiration_date else None,
        "is_active": p.is_active,
        "stock": qty,
    }


@router.get("")
def list_products(
    q: str | None = None,
    category_id: int | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    stmt = select(Product).where(Product.company_id == user.company_id)
    if q:
        like = f"%{q}%"
        stmt = stmt.where(or_(Product.name.ilike(like), Product.sku.ilike(like), Product.barcode.ilike(like)))
    if category_id:
        stmt = stmt.where(Product.category_id == category_id)
    products = db.scalars(stmt.order_by(Product.name)).all()
    stocks = {
        (b.product_id): float(b.qty_on_hand)
        for b in db.scalars(
            select(InventoryBalance).where(
                InventoryBalance.company_id == user.company_id,
                InventoryBalance.branch_id == user.branch_id,
            )
        )
    }
    return [_serialize(p, stocks.get(p.id, 0)) for p in products]


@router.get("/categories")
def categories(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = db.scalars(select(Category).where(Category.company_id == user.company_id)).all()
    return [{"id": c.id, "name": c.name} for c in rows]


@router.post("", dependencies=[Depends(require_permission("products.create"))])
def create_product(payload: ProductIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    p = Product(company_id=user.company_id, **payload.model_dump())
    db.add(p)
    db.commit()
    db.refresh(p)
    return _serialize(p, 0)


@router.patch("/{product_id}", dependencies=[Depends(require_permission("products.edit"))])
def update_product(product_id: int, payload: ProductIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    p = db.get(Product, product_id)
    if not p or p.company_id != user.company_id:
        raise HTTPException(404, "Producto no encontrado")
    for k, v in payload.model_dump().items():
        setattr(p, k, v)
    db.commit()
    return _serialize(p)
