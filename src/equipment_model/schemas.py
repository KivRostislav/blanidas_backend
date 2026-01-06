from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, relationship, mapped_column

from src.database import BaseDatabaseModel


class EquipmentModel(BaseDatabaseModel):
    __tablename__ = "equipment_model"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(unique=True)

    equipment: Mapped[list["Equipment"]] = relationship(back_populates="equipment_model", lazy="noload")
    spare_parts: Mapped[list["SparePart"]] = relationship(
        back_populates="compatible_models",
        secondary="equipment_model_spare_part",
        lazy="noload"
    )
