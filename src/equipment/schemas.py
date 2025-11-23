from datetime import date

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, relationship, mapped_column

from src.database import BaseDatabaseModel
from src.equipment_category.schemas import EquipmentCategory
from src.equipment_model.schemas import EquipmentModel
from src.institution.schemas import Institution
from src.manufacturer.schemas import Manufacturer


class Equipment(BaseDatabaseModel):
    __tablename__ = "equipment"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column()
    serial_number: Mapped[str] = mapped_column()
    installed: Mapped[date] = mapped_column()

    institution_id: Mapped[int] = mapped_column(ForeignKey("institution.id"))
    institution: Mapped["Institution"] = relationship(back_populates="equipment")

    equipment_model_id: Mapped[int] = mapped_column(ForeignKey("equipment_model.id"))
    equipment_model: Mapped["EquipmentModel"] = relationship(back_populates="equipment")

    equipment_category_id: Mapped[int] = mapped_column(ForeignKey("equipment_category.id"))
    equipment_category: Mapped["EquipmentCategory"] = relationship(back_populates="equipment")

    manufacturer_id: Mapped[int] = mapped_column(ForeignKey("manufacturer.id"))
    manufacturer: Mapped["Manufacturer"] = relationship(back_populates="equipment")

