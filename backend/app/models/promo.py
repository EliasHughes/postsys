from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.mixins import IdMixin, TimestampMixin


class Promotion(Base, IdMixin, TimestampMixin):
    __tablename__ = "promotions"

    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    name: Mapped[str] = mapped_column(String(120))
    kind: Mapped[str] = mapped_column(String(20))  # BXGY, PCT, AMOUNT, SPECIAL, COMBO
    value: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    buy_qty: Mapped[int] = mapped_column(default=0)
    get_qty: Mapped[int] = mapped_column(default=0)
    category_id: Mapped[int | None] = mapped_column(ForeignKey("product_categories.id"), nullable=True)
    customer_id: Mapped[int | None] = mapped_column(ForeignKey("customers.id"), nullable=True)
    starts_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    ends_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    hour_from: Mapped[str | None] = mapped_column(String(5), nullable=True)
    hour_to: Mapped[str | None] = mapped_column(String(5), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)


class LoyaltyAccount(Base, IdMixin, TimestampMixin):
    __tablename__ = "loyalty_accounts"

    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"))
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"), unique=True)
    points: Mapped[int] = mapped_column(default=0)
    tier: Mapped[str] = mapped_column(String(20), default="BRONZE")
