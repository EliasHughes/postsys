from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import IdMixin, TimestampMixin


class Company(Base, IdMixin, TimestampMixin):
    __tablename__ = "companies"

    name: Mapped[str] = mapped_column(String(160))
    legal_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    rnc: Mapped[str | None] = mapped_column(String(20), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(40), nullable=True)
    email: Mapped[str | None] = mapped_column(String(120), nullable=True)
    address: Mapped[str | None] = mapped_column(String(300), nullable=True)
    currency: Mapped[str] = mapped_column(String(8), default="DOP")
    tax_rate: Mapped[float] = mapped_column(default=0.18)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    branches: Mapped[list["Branch"]] = relationship(back_populates="company")


class Branch(Base, IdMixin, TimestampMixin):
    __tablename__ = "branches"

    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    name: Mapped[str] = mapped_column(String(160))
    code: Mapped[str] = mapped_column(String(20))
    address: Mapped[str | None] = mapped_column(String(300), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(40), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    company: Mapped[Company] = relationship(back_populates="branches")
    terminals: Mapped[list["Terminal"]] = relationship(back_populates="branch")


class Terminal(Base, IdMixin, TimestampMixin):
    __tablename__ = "terminals"

    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    branch_id: Mapped[int] = mapped_column(ForeignKey("branches.id"), index=True)
    name: Mapped[str] = mapped_column(String(80))
    code: Mapped[str] = mapped_column(String(20))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    branch: Mapped[Branch] = relationship(back_populates="terminals")
