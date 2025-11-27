from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, relationship, mapped_column

from src.database import BaseDatabaseModel


class EquipmentModel(BaseDatabaseModel):
    __tablename__ = "equipment_model"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column()

    equipment: Mapped[list["Equipment"]] = relationship(back_populates="equipment_model")
    spare_parts: Mapped[list["SparePart"]] = relationship(back_populates="compatible_models", secondary="equipment_model_spare_part")

class EquipmentModelSparePart(BaseDatabaseModel):
    __tablename__ = "equipment_model_spare_part"

    spare_part_id: Mapped[int] = mapped_column(ForeignKey("spare_part.id"), primary_key=True)
    equipment_model_id: Mapped[int] = mapped_column(ForeignKey("equipment_model.id"), primary_key=True)
