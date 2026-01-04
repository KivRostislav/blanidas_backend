from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, relationship, mapped_column

from src.database import BaseDatabaseModel
from src.institution.schemas import Institution


class SparePartLocationQuantity(BaseDatabaseModel):
    __tablename__ = "spare_part_location_quantity"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    quantity: Mapped[int] = mapped_column()

    institution_id: Mapped[int | None] = mapped_column(ForeignKey("institution.id", ondelete="CASCADE"), nullable=True)
    institution: Mapped["Institution"] = relationship(back_populates="spare_part_locations", lazy="noload")

    spare_part_id: Mapped[int | None] = mapped_column(ForeignKey("spare_part.id", ondelete="CASCADE"))
    spare_part: Mapped["SparePart"] = relationship(back_populates="locations", lazy="noload")


class SparePart(BaseDatabaseModel):
    __tablename__ = "spare_part"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column()
    serial_number: Mapped[str | None] = mapped_column(nullable=True)
    min_quantity: Mapped[int] = mapped_column()
    compatible_models: Mapped[list["EquipmentModel"]] = relationship(
        back_populates="spare_parts",
        secondary="equipment_model_spare_part",
        lazy="noload",
    )

    note: Mapped[str | None] = mapped_column(nullable=True)

    supplier_id: Mapped[int | None] = mapped_column(ForeignKey("supplier.id", ondelete="SET NULL"), nullable=True)
    supplier: Mapped["Supplier"] = relationship(back_populates="spare_parts", lazy="noload")

    locations: Mapped[list["SparePartLocationQuantity"]] = relationship(
        back_populates="spare_part",
        cascade="all, delete-orphan",
        lazy="noload",
    )

    spare_part_category_id: Mapped[int | None] = mapped_column(ForeignKey("spare_part_category.id", ondelete="SET NULL"), nullable=True)
    spare_part_category: Mapped["SparePartCategory"] = relationship(back_populates="spare_parts", lazy="noload")

    manufacturer_id: Mapped[int | None] = mapped_column(ForeignKey("manufacturer.id", ondelete="SET NULL"), nullable=True)
    manufacturer: Mapped["Manufacturer"] = relationship(back_populates="spare_parts", lazy="noload")

    used_spare_parts: Mapped[list["UsedSparePart"]] = relationship(back_populates="spare_part", lazy="noload")


