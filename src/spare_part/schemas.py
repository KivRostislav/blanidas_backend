from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, relationship, mapped_column

from src.database import BaseDatabaseModel
from src.equipment_model.schemas import EquipmentModel, EquipmentModelSparePart
from src.institution.schemas import Institution
from src.manufacturer.schemas import Manufacturer


class SparePart(BaseDatabaseModel):
    __tablename__ = "spare_part"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column()
    serial_number: Mapped[str | None] = mapped_column(nullable=True)
    price: Mapped[int] = mapped_column()
    quantity: Mapped[int] = mapped_column()
    min_quantity: Mapped[int] = mapped_column()
    compatible_models: Mapped[list["EquipmentModel"]] = relationship(
        back_populates="spare_parts",
        secondary=EquipmentModelSparePart.__table__,
    )

    note: Mapped[str | None] = mapped_column(nullable=True)

    supplier_id: Mapped[int] = mapped_column(ForeignKey("supplier.id"))
    supplier: Mapped["Supplier"] = relationship(back_populates="spare_parts")

    institution_id: Mapped[int] = mapped_column(ForeignKey("institution.id"))
    institution: Mapped["Institution"] = relationship(back_populates="spare_parts")

    spare_part_category_id: Mapped[int] = mapped_column(ForeignKey("spare_part_category.id"))
    spare_part_category: Mapped["SparePartCategory"] = relationship(back_populates="spare_parts")

    manufacturer_id: Mapped[int] = mapped_column(ForeignKey("manufacturer.id"))
    manufacturer: Mapped["Manufacturer"] = relationship(back_populates="spare_parts")


