from sqlalchemy import ForeignKey, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import Mapped, relationship, mapped_column

from src.database import BaseDatabaseModel
from src.institution.schemas import Institution


class Location(BaseDatabaseModel):
    __tablename__ = "location"
    __table_args__ = (
        UniqueConstraint("institution_id", "spare_part_id"),
        CheckConstraint("quantity >= 0", name="ck_location_quantity_positive"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    quantity: Mapped[int] = mapped_column()

    institution_id: Mapped[int | None] = mapped_column(ForeignKey("institution.id", ondelete="CASCADE"), nullable=True)
    institution: Mapped["Institution"] = relationship(back_populates="spare_part_locations", lazy="noload")

    spare_part_id: Mapped[int | None] = mapped_column(ForeignKey("spare_part.id", ondelete="CASCADE"))
    spare_part: Mapped["SparePart"] = relationship(back_populates="locations", lazy="noload")

class SparePart(BaseDatabaseModel):
    __tablename__ = "spare_part"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(unique=True)
    min_quantity: Mapped[int] = mapped_column()
    note: Mapped[str | None] = mapped_column(nullable=True)

    supplier_id: Mapped[int | None] = mapped_column(ForeignKey("supplier.id", ondelete="SET NULL"), nullable=True)
    supplier: Mapped["Supplier"] = relationship(back_populates="spare_parts", lazy="noload")

    spare_part_category_id: Mapped[int | None] = mapped_column(ForeignKey("spare_part_category.id", ondelete="SET NULL"), nullable=True)
    spare_part_category: Mapped["SparePartCategory"] = relationship(back_populates="spare_parts", lazy="noload")

    manufacturer_id: Mapped[int | None] = mapped_column(ForeignKey("manufacturer.id", ondelete="SET NULL"), nullable=True)
    manufacturer: Mapped["Manufacturer"] = relationship(back_populates="spare_parts", lazy="noload")

    locations: Mapped[list["Location"]] = relationship(back_populates="spare_part", lazy="noload")

    compatible_models: Mapped[list["EquipmentModel"]] = relationship(
        back_populates="spare_parts",
        secondary="equipment_model_spare_part",
        lazy="noload",
    )

    used_spare_parts: Mapped[list["UsedSparePart"]] = relationship(back_populates="spare_part", lazy="noload")

class EquipmentModelSparePart(BaseDatabaseModel):
    __tablename__ = "equipment_model_spare_part"

    spare_part_id: Mapped[int] = mapped_column(ForeignKey("spare_part.id", ondelete="CASCADE"), primary_key=True)
    equipment_model_id: Mapped[int] = mapped_column(ForeignKey("equipment_model.id", ondelete="CASCADE"), primary_key=True)

