from datetime import date
from typing import Optional, List

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from enum import Enum

from src.database import BaseDatabaseModel
from src.institution.schemas import Institution


def merge_enums(name: str, *enums: type[Enum]):
    values = {}
    for enum in enums:
        for item in enum:
            values[item.name] = item.value
    return Enum(name, values)

class Role(str, Enum):
    engineer = "engineer"
    manager = "manager"


class Scopes(str, Enum):
    edit_spare_part = "edit_spare_part"
    create_users = "create_users"

EngineerScopes = [Scopes.edit_spare_part]
ManagerScopes = [Scopes.create_users, Scopes.edit_spare_part]

class Scope(BaseDatabaseModel):
    __tablename__ = "scope"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    role: Mapped[Role] = mapped_column()

    users: Mapped[List["User"]] = relationship(back_populates="scopes", secondary="user_scope")

class UserScope(BaseDatabaseModel):
    __tablename__ = "user_scope"

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
    scope_id: Mapped[int] = mapped_column(ForeignKey("scope.id"), primary_key=True)

class User(BaseDatabaseModel):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column()
    password_hash: Mapped[str] = mapped_column()
    email: Mapped[str] = mapped_column(unique=True, index=True)
    phone_number: Mapped[str] = mapped_column()
    role: Mapped[Role] = mapped_column()
    scopes: Mapped[List[Scope]] = relationship(back_populates="users", secondary="user_scope")

    workplace_id: Mapped[Optional[int]] = mapped_column(ForeignKey("institution.id"), nullable=True)
    workplace: Mapped[Optional["Institution"]] = relationship(back_populates="users", lazy="noload")

    department: Mapped[str] = mapped_column()
    hire_at: Mapped[date] = mapped_column()

    receive_low_stock_notification: Mapped[bool] = mapped_column()
    receive_repair_request_creation_notification: Mapped[bool] = mapped_column()
