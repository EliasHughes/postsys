"""Capa Billing Engine — preparada para e-CF DGII (tipos 31,32,33,34,41,43,44,45).

La lógica fiscal NO vive dentro del POS. El POS llama a este motor.
"""
from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.mixins import IdMixin, TimestampMixin


class FiscalSequence(Base, IdMixin, TimestampMixin):
    __tablename__ = "fiscal_sequences"

    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    ecf_type: Mapped[str] = mapped_column(String(10))  # E31, E32, ...
    prefix: Mapped[str] = mapped_column(String(10))
    current: Mapped[int] = mapped_column(default=1)
    max_number: Mapped[int] = mapped_column(default=99999999)
    is_active: Mapped[bool] = mapped_column(default=True)


class ElectronicInvoice(Base, IdMixin, TimestampMixin):
    __tablename__ = "electronic_invoices"

    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    sale_id: Mapped[int | None] = mapped_column(ForeignKey("sales.id"), nullable=True)
    ecf_type: Mapped[str] = mapped_column(String(10))
    e_ncf: Mapped[str] = mapped_column(String(20), unique=True)
    status: Mapped[str] = mapped_column(String(30), default="DRAFT")
    # DRAFT, SIGNED, SENT, ACCEPTED, REJECTED, CONTINGENCY
    xml_payload: Mapped[str | None] = mapped_column(Text, nullable=True)
    dgii_track_id: Mapped[str | None] = mapped_column(String(80), nullable=True)
    dgii_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    signed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
