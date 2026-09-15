from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import IdMixin, TimestampMixin


class Sale(Base, IdMixin, TimestampMixin):
    """
    Ciclo: DRAFT → CONFIRMED → PAID → INVOICED
    Alternos: SUSPENDED, CANCELLED, RETURNED
    """
    __tablename__ = "sales"

    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    branch_id: Mapped[int] = mapped_column(ForeignKey("branches.id"), index=True)
    terminal_id: Mapped[int | None] = mapped_column(ForeignKey("terminals.id"), nullable=True)
    cash_session_id: Mapped[int | None] = mapped_column(ForeignKey("cash_sessions.id"), nullable=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    customer_id: Mapped[int | None] = mapped_column(ForeignKey("customers.id"), nullable=True)

    number: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    status: Mapped[str] = mapped_column(String(20), default="DRAFT", index=True)
    sold_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    subtotal: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    discount_global: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    tax_total: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    total: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    paid_total: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    change_amount: Mapped[float] = mapped_column(Numeric(14, 2), default=0)

    ncf: Mapped[str | None] = mapped_column(String(20), nullable=True)
    ecf_type: Mapped[str | None] = mapped_column(String(10), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    details: Mapped[list["SaleDetail"]] = relationship(back_populates="sale", cascade="all, delete-orphan")
    payments: Mapped[list["SalePayment"]] = relationship(back_populates="sale", cascade="all, delete-orphan")
    taxes: Mapped[list["SaleTax"]] = relationship(back_populates="sale", cascade="all, delete-orphan")


class SaleDetail(Base, IdMixin):
    __tablename__ = "sale_details"

    sale_id: Mapped[int] = mapped_column(ForeignKey("sales.id"), index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    description: Mapped[str] = mapped_column(String(160))
    qty: Mapped[float] = mapped_column(Numeric(14, 3))
    unit_price: Mapped[float] = mapped_column(Numeric(14, 4))
    discount: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    tax_rate: Mapped[float] = mapped_column(Numeric(7, 4), default=0.18)
    tax_amount: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    line_total: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    cost: Mapped[float] = mapped_column(Numeric(14, 4), default=0)

    sale: Mapped[Sale] = relationship(back_populates="details")


class SalePayment(Base, IdMixin):
    __tablename__ = "sale_payments"

    sale_id: Mapped[int] = mapped_column(ForeignKey("sales.id"), index=True)
    method: Mapped[str] = mapped_column(String(20))  # CASH, CARD, TRANSFER, CHECK, CREDIT, OTHER
    amount: Mapped[float] = mapped_column(Numeric(14, 2))
    reference: Mapped[str | None] = mapped_column(String(80), nullable=True)

    sale: Mapped[Sale] = relationship(back_populates="payments")


class SaleTax(Base, IdMixin):
    __tablename__ = "sale_taxes"

    sale_id: Mapped[int] = mapped_column(ForeignKey("sales.id"), index=True)
    name: Mapped[str] = mapped_column(String(40))
    rate: Mapped[float] = mapped_column(Numeric(7, 4))
    amount: Mapped[float] = mapped_column(Numeric(14, 2))

    sale: Mapped[Sale] = relationship(back_populates="taxes")


class Quote(Base, IdMixin, TimestampMixin):
    __tablename__ = "quotes"

    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    branch_id: Mapped[int] = mapped_column(ForeignKey("branches.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    customer_id: Mapped[int | None] = mapped_column(ForeignKey("customers.id"), nullable=True)
    number: Mapped[str] = mapped_column(String(30), unique=True)
    status: Mapped[str] = mapped_column(String(20), default="DRAFT")  # DRAFT, SENT, CONVERTED, EXPIRED
    subtotal: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    tax_total: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    total: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    converted_sale_id: Mapped[int | None] = mapped_column(ForeignKey("sales.id"), nullable=True)

    details: Mapped[list["QuoteDetail"]] = relationship(back_populates="quote", cascade="all, delete-orphan")


class QuoteDetail(Base, IdMixin):
    __tablename__ = "quote_details"

    quote_id: Mapped[int] = mapped_column(ForeignKey("quotes.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    description: Mapped[str] = mapped_column(String(160))
    qty: Mapped[float] = mapped_column(Numeric(14, 3))
    unit_price: Mapped[float] = mapped_column(Numeric(14, 4))
    line_total: Mapped[float] = mapped_column(Numeric(14, 2))

    quote: Mapped[Quote] = relationship(back_populates="details")


class ReturnDoc(Base, IdMixin, TimestampMixin):
    __tablename__ = "returns"

    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    branch_id: Mapped[int] = mapped_column(ForeignKey("branches.id"))
    sale_id: Mapped[int] = mapped_column(ForeignKey("sales.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    number: Mapped[str] = mapped_column(String(30), unique=True)
    status: Mapped[str] = mapped_column(String(20), default="POSTED")
    total: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    reason: Mapped[str | None] = mapped_column(String(200), nullable=True)

    details: Mapped[list["ReturnDetail"]] = relationship(back_populates="return_doc", cascade="all, delete-orphan")


class ReturnDetail(Base, IdMixin):
    __tablename__ = "return_details"

    return_id: Mapped[int] = mapped_column(ForeignKey("returns.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    qty: Mapped[float] = mapped_column(Numeric(14, 3))
    amount: Mapped[float] = mapped_column(Numeric(14, 2))

    return_doc: Mapped[ReturnDoc] = relationship(back_populates="details")
