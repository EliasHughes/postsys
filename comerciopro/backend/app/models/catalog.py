from sqlalchemy import Boolean, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.mixins import IdMixin, TimestampMixin


class Category(Base, IdMixin, TimestampMixin):
    __tablename__ = "product_categories"

    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    name: Mapped[str] = mapped_column(String(80))
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("product_categories.id"), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class Brand(Base, IdMixin, TimestampMixin):
    __tablename__ = "product_brands"

    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    name: Mapped[str] = mapped_column(String(80))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class UnitOfMeasure(Base, IdMixin):
    __tablename__ = "units_of_measure"

    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    code: Mapped[str] = mapped_column(String(10))
    name: Mapped[str] = mapped_column(String(40))


class TaxRate(Base, IdMixin):
    __tablename__ = "product_taxes"

    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    name: Mapped[str] = mapped_column(String(40))
    rate: Mapped[float] = mapped_column(Numeric(7, 4))
    is_exempt: Mapped[bool] = mapped_column(Boolean, default=False)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
