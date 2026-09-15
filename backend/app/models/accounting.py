from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import IdMixin, TimestampMixin


class Account(Base, IdMixin, TimestampMixin):
    __tablename__ = "accounts"

    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    code: Mapped[str] = mapped_column(String(20), index=True)
    name: Mapped[str] = mapped_column(String(160))
    type: Mapped[str] = mapped_column(String(20))  # ASSET, LIABILITY, EQUITY, INCOME, COST, EXPENSE
    nature: Mapped[str] = mapped_column(String(10))  # DEBIT, CREDIT
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("accounts.id"), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)


class JournalEntry(Base, IdMixin, TimestampMixin):
    __tablename__ = "journal_entries"

    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    branch_id: Mapped[int | None] = mapped_column(ForeignKey("branches.id"), nullable=True)
    number: Mapped[str] = mapped_column(String(30), unique=True)
    source: Mapped[str] = mapped_column(String(30))  # SALE, PURCHASE, PAYMENT, EXPENSE, RETURN, MANUAL, CASH
    source_id: Mapped[str | None] = mapped_column(String(40), nullable=True)
    concept: Mapped[str] = mapped_column(String(200))
    posted_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    status: Mapped[str] = mapped_column(String(20), default="POSTED")
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)

    lines: Mapped[list["JournalEntryLine"]] = relationship(back_populates="entry", cascade="all, delete-orphan")


class JournalEntryLine(Base, IdMixin):
    __tablename__ = "journal_entry_details"

    entry_id: Mapped[int] = mapped_column(ForeignKey("journal_entries.id"), index=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"))
    debit: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    credit: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    memo: Mapped[str | None] = mapped_column(String(200), nullable=True)

    entry: Mapped[JournalEntry] = relationship(back_populates="lines")
    account: Mapped[Account] = relationship()


class AccountReceivable(Base, IdMixin, TimestampMixin):
    __tablename__ = "accounts_receivable"

    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"))
    sale_id: Mapped[int | None] = mapped_column(ForeignKey("sales.id"), nullable=True)
    number: Mapped[str] = mapped_column(String(30))
    original_amount: Mapped[float] = mapped_column(Numeric(14, 2))
    balance: Mapped[float] = mapped_column(Numeric(14, 2))
    due_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="OPEN")


class AccountPayable(Base, IdMixin, TimestampMixin):
    __tablename__ = "accounts_payable"

    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    supplier_id: Mapped[int] = mapped_column(ForeignKey("suppliers.id"))
    purchase_id: Mapped[int | None] = mapped_column(ForeignKey("purchases.id"), nullable=True)
    number: Mapped[str] = mapped_column(String(30))
    original_amount: Mapped[float] = mapped_column(Numeric(14, 2))
    balance: Mapped[float] = mapped_column(Numeric(14, 2))
    due_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="OPEN")
