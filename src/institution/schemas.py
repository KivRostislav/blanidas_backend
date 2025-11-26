from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, relationship, mapped_column

from src.database import BaseDatabaseModel


class Institution(BaseDatabaseModel):
    __tablename__ = "institution"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column()
    address: Mapped[str] = mapped_column()

    institution_type_id: Mapped[int] = mapped_column(ForeignKey("institution_type.id"))
    institution_type: Mapped["InstitutionType"] = relationship(back_populates="institutions", lazy="noload")

    equipment: Mapped[list["Equipment"]] = relationship(back_populates="institution")

    contact_email: Mapped[str] = mapped_column()
    contact_phone: Mapped[str] = mapped_column()
