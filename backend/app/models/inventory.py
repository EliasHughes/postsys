from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.mixins import IdMixin, TimestampMixin


class InventoryBalance(Base, IdMixin, TimestampMixin):
    """Existencia por sucursal: actual / disponible / reservada."""
    __tablename__ = "inventory"

    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    branch_id: Mapped[int] = mapped_column(ForeignKey("branches.id"), index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), index=True)
    qty_on_hand: Mapped[float] = mapped_column(Numeric(14, 3), default=0)
    qty_reserved: Mapped[float] = mapped_column(Numeric(14, 3), default=0)
    avg_cost: Mapped[float] = mapped_column(Numeric(14, 4), default=0)

    @property
    def qty_available(self) -> float:
        return float(self.qty_on_hand) - float(self.qty_reserved)


class InventoryMovement(Base, IdMixin):
    """Kardex."""
    __tablename__ = "inventory_movements"

    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    branch_id: Mapped[int] = mapped_column(ForeignKey("branches.id"), index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), index=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    moved_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    movement_type: Mapped[str] = mapped_column(String(30))  # IN, OUT, ADJUST, TRANSFER, RETURN, LOSS, SALE, PURCHASE
    qty: Mapped[float] = mapped_column(Numeric(14, 3))
    cost: Mapped[float] = mapped_column(Numeric(14, 4), default=0)
    qty_before: Mapped[float] = mapped_column(Numeric(14, 3))
    qty_after: Mapped[float] = mapped_column(Numeric(14, 3))
    source_doc: Mapped[str | None] = mapped_column(String(40), nullable=True)
    reason: Mapped[str | None] = mapped_column(String(200), nullable=True)


class InventoryTransfer(Base, IdMixin, TimestampMixin):
    __tablename__ = "inventory_transfers"

    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    number: Mapped[str] = mapped_column(String(30), unique=True)
    from_branch_id: Mapped[int] = mapped_column(ForeignKey("branches.id"))
    to_branch_id: Mapped[int] = mapped_column(ForeignKey("branches.id"))
    status: Mapped[str] = mapped_column(String(20), default="DRAFT")  # DRAFT, SENT, RECEIVED, CANCELLED
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)


class InventoryAdjustment(Base, IdMixin, TimestampMixin):
    __tablename__ = "inventory_adjustments"

    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    branch_id: Mapped[int] = mapped_column(ForeignKey("branches.id"))
    number: Mapped[str] = mapped_column(String(30), unique=True)
    reason: Mapped[str] = mapped_column(String(200))
    status: Mapped[str] = mapped_column(String(20), default="POSTED")
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
