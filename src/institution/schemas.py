from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, relationship, mapped_column

from src.database import BaseDatabaseModel


class Institution(BaseDatabaseModel):
    __tablename__ = "institution"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column()
    address: Mapped[str] = mapped_column()

    institution_type_id: Mapped[int | None] = mapped_column(ForeignKey("institution_type.id", ondelete="SET NULL"), nullable=True)
    institution_type: Mapped["InstitutionType"] = relationship(back_populates="institutions", lazy="noload")

    equipment: Mapped[list["Equipment"]] = relationship(back_populates="institution", lazy="noload")
    users: Mapped[list["User"]] = relationship(back_populates="workplace", lazy="noload")

    contact_email: Mapped[str] = mapped_column()
    contact_phone: Mapped[str] = mapped_column()

    used_spare_parts: Mapped[list["UsedSparePart"]] = relationship(back_populates="institution", lazy="noload")
    spare_part_locations: Mapped[list["SparePartLocationQuantity"]] = relationship(
        back_populates="institution",
        lazy="noload",
        cascade="all, delete-orphan",
    )

