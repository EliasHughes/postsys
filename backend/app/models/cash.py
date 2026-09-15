from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import IdMixin, TimestampMixin


class CashRegister(Base, IdMixin, TimestampMixin):
    __tablename__ = "cash_registers"

    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    branch_id: Mapped[int] = mapped_column(ForeignKey("branches.id"), index=True)
    name: Mapped[str] = mapped_column(String(80))
    code: Mapped[str] = mapped_column(String(20))
    is_active: Mapped[bool] = mapped_column(default=True)

    sessions: Mapped[list["CashSession"]] = relationship(back_populates="register")


class CashSession(Base, IdMixin, TimestampMixin):
    __tablename__ = "cash_sessions"

    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    branch_id: Mapped[int] = mapped_column(ForeignKey("branches.id"))
    register_id: Mapped[int] = mapped_column(ForeignKey("cash_registers.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    opened_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    closed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="OPEN")  # OPEN, CLOSED

    opening_float: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    expected_cash: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    counted_cash: Mapped[float | None] = mapped_column(Numeric(14, 2), nullable=True)
    difference: Mapped[float] = mapped_column(Numeric(14, 2), default=0)

    register: Mapped[CashRegister] = relationship(back_populates="sessions")
    movements: Mapped[list["CashMovement"]] = relationship(back_populates="session")


class CashMovement(Base, IdMixin):
    __tablename__ = "cash_movements"

    session_id: Mapped[int] = mapped_column(ForeignKey("cash_sessions.id"), index=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"))
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    moved_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    kind: Mapped[str] = mapped_column(String(30))
    # SALE_CASH, SALE_CARD, SALE_TRANSFER, REFUND, EXPENSE, IN, WITHDRAW, DEPOSIT
    method: Mapped[str] = mapped_column(String(20), default="CASH")
    amount: Mapped[float] = mapped_column(Numeric(14, 2))
    reference: Mapped[str | None] = mapped_column(String(80), nullable=True)
    notes: Mapped[str | None] = mapped_column(String(200), nullable=True)

    session: Mapped[CashSession] = relationship(back_populates="movements")
