from datetime import datetime
from sqlalchemy import Boolean, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import IdMixin, TimestampMixin


class Permission(Base, IdMixin):
    __tablename__ = "permissions"

    code: Mapped[str] = mapped_column(String(80), unique=True)
    module: Mapped[str] = mapped_column(String(40))
    description: Mapped[str | None] = mapped_column(String(200), nullable=True)


class Role(Base, IdMixin, TimestampMixin):
    __tablename__ = "roles"

    company_id: Mapped[int | None] = mapped_column(ForeignKey("companies.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(80))
    slug: Mapped[str] = mapped_column(String(40))
    description: Mapped[str | None] = mapped_column(String(200), nullable=True)
    is_system: Mapped[bool] = mapped_column(Boolean, default=False)

    permissions: Mapped[list[Permission]] = relationship(secondary="role_permissions")


class RolePermission(Base, IdMixin):
    __tablename__ = "role_permissions"
    __table_args__ = (UniqueConstraint("role_id", "permission_id"),)

    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"))
    permission_id: Mapped[int] = mapped_column(ForeignKey("permissions.id"))


class User(Base, IdMixin, TimestampMixin):
    __tablename__ = "users"

    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    branch_id: Mapped[int | None] = mapped_column(ForeignKey("branches.id"), nullable=True)
    username: Mapped[str] = mapped_column(String(60), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(160))
    email: Mapped[str | None] = mapped_column(String(160), nullable=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    roles: Mapped[list[Role]] = relationship(secondary="user_roles")

    def permission_codes(self) -> set[str]:
        codes: set[str] = set()
        for role in self.roles:
            if role.slug in {"super_admin"}:
                codes.add("*")
            for perm in role.permissions:
                codes.add(perm.code)
        return codes

    def has_permission(self, code: str) -> bool:
        codes = self.permission_codes()
        return "*" in codes or code in codes


class UserRole(Base, IdMixin):
    __tablename__ = "user_roles"
    __table_args__ = (UniqueConstraint("user_id", "role_id"),)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"))


class RefreshToken(Base, IdMixin):
    __tablename__ = "refresh_tokens"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    token: Mapped[str] = mapped_column(String(500), unique=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime)
    revoked: Mapped[bool] = mapped_column(Boolean, default=False)
