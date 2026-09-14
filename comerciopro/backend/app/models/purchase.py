from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import IdMixin, TimestampMixin


class Purchase(Base, IdMixin, TimestampMixin):
    """DRAFT → PENDING → APPROVED → RECEIVED / PARTIAL → ACCOUNTED → PAID | CANCELLED"""
    __tablename__ = "purchases"

    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    branch_id: Mapped[int] = mapped_column(ForeignKey("branches.id"))
    supplier_id: Mapped[int] = mapped_column(ForeignKey("suppliers.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    number: Mapped[str] = mapped_column(String(30), unique=True)
    status: Mapped[str] = mapped_column(String(20), default="DRAFT", index=True)
    ordered_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    subtotal: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    tax_total: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    total: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    details: Mapped[list["PurchaseDetail"]] = relationship(back_populates="purchase", cascade="all, delete-orphan")
    payments: Mapped[list["PurchasePayment"]] = relationship(back_populates="purchase")


class PurchaseDetail(Base, IdMixin):
    __tablename__ = "purchase_details"

    purchase_id: Mapped[int] = mapped_column(ForeignKey("purchases.id"), index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    description: Mapped[str] = mapped_column(String(160))
    qty: Mapped[float] = mapped_column(Numeric(14, 3))
    qty_received: Mapped[float] = mapped_column(Numeric(14, 3), default=0)
    unit_cost: Mapped[float] = mapped_column(Numeric(14, 4))
    tax_rate: Mapped[float] = mapped_column(Numeric(7, 4), default=0.18)
    tax_amount: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    line_total: Mapped[float] = mapped_column(Numeric(14, 2), default=0)

    purchase: Mapped[Purchase] = relationship(back_populates="details")


class PurchasePayment(Base, IdMixin, TimestampMixin):
    __tablename__ = "purchase_payments"

    purchase_id: Mapped[int] = mapped_column(ForeignKey("purchases.id"))
    method: Mapped[str] = mapped_column(String(20))
    amount: Mapped[float] = mapped_column(Numeric(14, 2))
    reference: Mapped[str | None] = mapped_column(String(80), nullable=True)

    purchase: Mapped[Purchase] = relationship(back_populates="payments")


class GoodsReceipt(Base, IdMixin, TimestampMixin):
    __tablename__ = "goods_receipts"

    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"))
    branch_id: Mapped[int] = mapped_column(ForeignKey("branches.id"))
    purchase_id: Mapped[int] = mapped_column(ForeignKey("purchases.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    number: Mapped[str] = mapped_column(String(30), unique=True)
    received_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    details: Mapped[list["GoodsReceiptDetail"]] = relationship(back_populates="receipt", cascade="all, delete-orphan")


class GoodsReceiptDetail(Base, IdMixin):
    __tablename__ = "goods_receipt_details"

    receipt_id: Mapped[int] = mapped_column(ForeignKey("goods_receipts.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    qty: Mapped[float] = mapped_column(Numeric(14, 3))
    unit_cost: Mapped[float] = mapped_column(Numeric(14, 4))

    receipt: Mapped[GoodsReceipt] = relationship(back_populates="details")
