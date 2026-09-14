from sqlalchemy import Boolean, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import IdMixin, TimestampMixin


class Customer(Base, IdMixin, TimestampMixin):
    __tablename__ = "customers"

    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    name: Mapped[str] = mapped_column(String(160))
    document_type: Mapped[str] = mapped_column(String(20), default="CEDULA")  # CEDULA, RNC, PASAPORTE
    document: Mapped[str | None] = mapped_column(String(30), nullable=True, index=True)
    phone: Mapped[str | None] = mapped_column(String(40), nullable=True)
    email: Mapped[str | None] = mapped_column(String(160), nullable=True)
    credit_limit: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    balance: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    loyalty_points: Mapped[int] = mapped_column(default=0)
    is_final_consumer: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    addresses: Mapped[list["CustomerAddress"]] = relationship(back_populates="customer")


class CustomerAddress(Base, IdMixin):
    __tablename__ = "customer_addresses"

    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"))
    line: Mapped[str] = mapped_column(String(300))
    city: Mapped[str | None] = mapped_column(String(80), nullable=True)
    is_default: Mapped[bool] = mapped_column(Boolean, default=True)

    customer: Mapped[Customer] = relationship(back_populates="addresses")


class Supplier(Base, IdMixin, TimestampMixin):
    __tablename__ = "suppliers"

    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    name: Mapped[str] = mapped_column(String(160))
    rnc: Mapped[str | None] = mapped_column(String(20), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(40), nullable=True)
    email: Mapped[str | None] = mapped_column(String(160), nullable=True)
    balance: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    addresses: Mapped[list["SupplierAddress"]] = relationship(back_populates="supplier")


class SupplierAddress(Base, IdMixin):
    __tablename__ = "supplier_addresses"

    supplier_id: Mapped[int] = mapped_column(ForeignKey("suppliers.id"))
    line: Mapped[str] = mapped_column(String(300))
    city: Mapped[str | None] = mapped_column(String(80), nullable=True)

    supplier: Mapped[Supplier] = relationship(back_populates="addresses")
