from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.cash import CashMovement, CashSession
from app.models.accounting import AccountReceivable
from app.models.product import Product
from app.models.sale import Sale, SaleDetail, SalePayment, SaleTax
from app.models.user import User
from app.schemas.sales import SaleCreate
from app.services.accounting import post_sale_entry
from app.services.audit import log_action
from app.services.inventory import apply_movement
from app.services.sequences import next_sale_number


def _tax_rate(product: Product, default: float = 0.18) -> float:
    if product.tax is not None:
        return 0.0 if product.tax.is_exempt else float(product.tax.rate)
    return default


def create_sale(db: Session, payload: SaleCreate, user: User, ip: str | None = None) -> Sale:
    """
    Transacción atómica:
    Sale + Details + Payments + InventoryMovement + CashMovement + Accounting + Audit
    """
    branch_id = payload.branch_id or user.branch_id
    if not branch_id:
        raise HTTPException(status_code=400, detail="Sucursal requerida")

    session: CashSession | None = None
    if payload.cash_session_id:
        session = db.get(CashSession, payload.cash_session_id)
        if not session or session.status != "OPEN":
            raise HTTPException(status_code=400, detail="No hay sesión de caja abierta")

    if not payload.items:
        raise HTTPException(status_code=400, detail="La venta no tiene productos")

    sale = Sale(
        company_id=user.company_id,
        branch_id=branch_id,
        cash_session_id=session.id if session else None,
        user_id=user.id,
        customer_id=payload.customer_id,
        number=next_sale_number(db, user.company_id),
        status="CONFIRMED",
        discount_global=payload.discount_global,
        notes=payload.notes,
        ecf_type=payload.ecf_type,
    )
    db.add(sale)
    db.flush()

    subtotal = 0.0
    tax_total = 0.0
    cogs = 0.0

    for line in payload.items:
        product = db.get(Product, line.product_id)
        if not product or not product.is_active:
            raise HTTPException(status_code=400, detail=f"Producto {line.product_id} no disponible")
        price = float(line.unit_price if line.unit_price is not None else product.price)
        line_net = max(0.0, (price * line.qty) - line.discount)
        rate = _tax_rate(product)
        tax_amt = round(line_net * rate, 2)
        line_total = round(line_net + tax_amt, 2)

        db.add(
            SaleDetail(
                sale_id=sale.id,
                product_id=product.id,
                description=product.name,
                qty=line.qty,
                unit_price=price,
                discount=line.discount,
                tax_rate=rate,
                tax_amount=tax_amt,
                line_total=line_total,
                cost=float(product.cost),
            )
        )
        subtotal += price * line.qty
        tax_total += tax_amt
        cogs += float(product.cost) * line.qty

        apply_movement(
            db,
            company_id=user.company_id,
            branch_id=branch_id,
            product_id=product.id,
            user_id=user.id,
            movement_type="SALE",
            qty=-line.qty,
            cost=float(product.cost),
            source_doc=sale.number,
            reason="Venta POS",
        )

    taxable_base = max(0.0, subtotal - payload.discount_global)
    # Recalcular ITBIS sobre base con descuento global proporcional
    if subtotal > 0 and payload.discount_global:
        factor = taxable_base / subtotal
        tax_total = round(tax_total * factor, 2)

    total = round(taxable_base + tax_total, 2)
    paid = sum(p.amount for p in payload.payments)
    if paid + 0.009 < total and not any(p.method == "CREDIT" for p in payload.payments):
        raise HTTPException(status_code=400, detail="El pago no cubre el total")

    sale.subtotal = round(subtotal, 2)
    sale.tax_total = tax_total
    sale.total = total
    sale.paid_total = round(paid, 2)
    sale.change_amount = max(0.0, round(paid - total, 2))
    sale.status = "PAID" if paid >= total or any(p.method == "CREDIT" for p in payload.payments) else "CONFIRMED"

    methods_seen: dict[str, float] = {}
    for pay in payload.payments:
        db.add(
            SalePayment(
                sale_id=sale.id,
                method=pay.method,
                amount=pay.amount,
                reference=pay.reference,
            )
        )
        methods_seen[pay.method] = methods_seen.get(pay.method, 0) + pay.amount
        if session:
            kind_map = {
                "CASH": "SALE_CASH",
                "CARD": "SALE_CARD",
                "TRANSFER": "SALE_TRANSFER",
                "CHECK": "SALE_CHECK",
                "CREDIT": "SALE_CREDIT",
                "OTHER": "SALE_OTHER",
            }
            db.add(
                CashMovement(
                    session_id=session.id,
                    company_id=user.company_id,
                    user_id=user.id,
                    kind=kind_map.get(pay.method, "SALE_OTHER"),
                    method=pay.method,
                    amount=pay.amount if pay.method != "CASH" else max(0, pay.amount - sale.change_amount),
                    reference=sale.number,
                )
            )

    if tax_total:
        db.add(SaleTax(sale_id=sale.id, name="ITBIS", rate=0.18, amount=tax_total))

    credit_amt = methods_seen.get("CREDIT", 0)
    if credit_amt:
        db.add(
            AccountReceivable(
                company_id=user.company_id,
                customer_id=payload.customer_id or 0,
                sale_id=sale.id,
                number=sale.number,
                original_amount=credit_amt,
                balance=credit_amt,
                status="OPEN",
            )
        )
        if not payload.customer_id:
            raise HTTPException(status_code=400, detail="Venta a crédito requiere cliente")

    post_sale_entry(db, sale, cogs=round(cogs, 2))
    log_action(
        db,
        user_id=user.id,
        company_id=user.company_id,
        branch_id=branch_id,
        ip=ip,
        module="sales",
        action="create",
        entity="Sale",
        entity_id=sale.number,
        new_value=str(total),
        message=f"Venta {sale.number}",
    )
    db.commit()
    db.refresh(sale)
    return sale
