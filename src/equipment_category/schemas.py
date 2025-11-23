from sqlalchemy.orm import Mapped, relationship, mapped_column

from src.database import BaseDatabaseModel


class EquipmentCategory(BaseDatabaseModel):
    __tablename__ = "equipment_category"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column()

    equipment: Mapped[list["Equipment"]] = relationship(back_populates="equipment_category")
