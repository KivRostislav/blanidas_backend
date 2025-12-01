from datetime import date

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, relationship, mapped_column

from src.database import BaseDatabaseModel
from src.equipment_category.schemas import EquipmentCategory
from src.equipment_model.schemas import EquipmentModel
from src.institution.schemas import Institution
from src.manufacturer.schemas import Manufacturer
from src.models import StringToDate


class Equipment(BaseDatabaseModel):
    __tablename__ = "equipment"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column()
    serial_number: Mapped[str] = mapped_column()
    installed: Mapped[date] = mapped_column(StringToDate)

    institution_id: Mapped[int | None] = mapped_column(ForeignKey("institution.id"), nullable=True)
    institution: Mapped["Institution"] = relationship(back_populates="equipment", lazy="raise")

    equipment_model_id: Mapped[int | None] = mapped_column(ForeignKey("equipment_model.id"), nullable=True)
    equipment_model: Mapped["EquipmentModel"] = relationship(back_populates="equipment", lazy="raise")

    equipment_category_id: Mapped[int | None] = mapped_column(ForeignKey("equipment_category.id"), nullable=True)
    equipment_category: Mapped["EquipmentCategory"] = relationship(back_populates="equipment", lazy="raise")

    manufacturer_id: Mapped[int | None] = mapped_column(ForeignKey("manufacturer.id"), nullable=True)
    manufacturer: Mapped["Manufacturer"] = relationship(back_populates="equipment", lazy="raise")

