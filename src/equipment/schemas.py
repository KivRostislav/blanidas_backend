from datetime import date

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, relationship, mapped_column

from src.database import BaseDatabaseModel
from src.models import StringToDate


class Equipment(BaseDatabaseModel):
    __tablename__ = "equipment"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column()
    serial_number: Mapped[str] = mapped_column()
    installed: Mapped[date] = mapped_column(StringToDate)

    institution_id: Mapped[int | None] = mapped_column(ForeignKey("institution.id"), nullable=True)
    institution: Mapped["Institution"] = relationship(back_populates="equipment", lazy="noload")

    equipment_model_id: Mapped[int | None] = mapped_column(ForeignKey("equipment_model.id"), nullable=True)
    equipment_model: Mapped["EquipmentModel"] = relationship(back_populates="equipment", lazy="noload")

    equipment_category_id: Mapped[int | None] = mapped_column(ForeignKey("equipment_category.id"), nullable=True)
    equipment_category: Mapped["EquipmentCategory"] = relationship(back_populates="equipment", lazy="noload")

    manufacturer_id: Mapped[int | None] = mapped_column(ForeignKey("manufacturer.id"), nullable=True)
    manufacturer: Mapped["Manufacturer"] = relationship(back_populates="equipment", lazy="noload")

    repair_requests: Mapped[list["RepairRequest"]] = relationship(back_populates="equipment", lazy="noload")

