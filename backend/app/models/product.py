from datetime import date
from sqlalchemy import Boolean, Date, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import IdMixin, TimestampMixin


class Product(Base, IdMixin, TimestampMixin):
    __tablename__ = "products"

    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    sku: Mapped[str] = mapped_column(String(40), index=True)
    barcode: Mapped[str | None] = mapped_column(String(40), index=True, nullable=True)
    name: Mapped[str] = mapped_column(String(160))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category_id: Mapped[int | None] = mapped_column(ForeignKey("product_categories.id"), nullable=True)
    brand_id: Mapped[int | None] = mapped_column(ForeignKey("product_brands.id"), nullable=True)
    unit_id: Mapped[int | None] = mapped_column(ForeignKey("units_of_measure.id"), nullable=True)
    tax_id: Mapped[int | None] = mapped_column(ForeignKey("product_taxes.id"), nullable=True)
    supplier_id: Mapped[int | None] = mapped_column(ForeignKey("suppliers.id"), nullable=True)

    cost: Mapped[float] = mapped_column(Numeric(14, 4), default=0)
    price: Mapped[float] = mapped_column(Numeric(14, 4), default=0)
    wholesale_price: Mapped[float | None] = mapped_column(Numeric(14, 4), nullable=True)
    min_price: Mapped[float | None] = mapped_column(Numeric(14, 4), nullable=True)

    min_stock: Mapped[float] = mapped_column(Numeric(14, 3), default=0)
    max_stock: Mapped[float] = mapped_column(Numeric(14, 3), default=0)
    reorder_point: Mapped[float] = mapped_column(Numeric(14, 3), default=0)
    location: Mapped[str | None] = mapped_column(String(80), nullable=True)
    image_url: Mapped[str | None] = mapped_column(String(300), nullable=True)
    expiration_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    lot: Mapped[str | None] = mapped_column(String(40), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    category = relationship("Category")
    tax = relationship("TaxRate")
    prices: Mapped[list["ProductPrice"]] = relationship(back_populates="product")


class ProductPrice(Base, IdMixin):
    __tablename__ = "product_prices"

    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), index=True)
    name: Mapped[str] = mapped_column(String(40))  # regular, wholesale, special
    price: Mapped[float] = mapped_column(Numeric(14, 4))

    product: Mapped[Product] = relationship(back_populates="prices")
