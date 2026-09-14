from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.mixins import IdMixin


class AuditLog(Base, IdMixin):
    __tablename__ = "audit_logs"

    company_id: Mapped[int | None] = mapped_column(ForeignKey("companies.id"), nullable=True, index=True)
    branch_id: Mapped[int | None] = mapped_column(ForeignKey("branches.id"), nullable=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), index=True)
    ip: Mapped[str | None] = mapped_column(String(60), nullable=True)
    module: Mapped[str] = mapped_column(String(40))
    action: Mapped[str] = mapped_column(String(40))
    entity: Mapped[str | None] = mapped_column(String(60), nullable=True)
    entity_id: Mapped[str | None] = mapped_column(String(40), nullable=True)
    old_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    new_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    result: Mapped[str] = mapped_column(String(20), default="OK")
    message: Mapped[str | None] = mapped_column(String(300), nullable=True)


class SystemSetting(Base, IdMixin):
    __tablename__ = "system_settings"

    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    key: Mapped[str] = mapped_column(String(80))
    value: Mapped[str] = mapped_column(Text)


class Notification(Base, IdMixin):
    __tablename__ = "notifications"

    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    level: Mapped[str] = mapped_column(String(20))  # critical, warning, info, success
    kind: Mapped[str] = mapped_column(String(40))
    title: Mapped[str] = mapped_column(String(160))
    body: Mapped[str | None] = mapped_column(String(400), nullable=True)
    is_read: Mapped[bool] = mapped_column(default=False)
