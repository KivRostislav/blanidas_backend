from datetime import date

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, relationship, mapped_column

from src.database import BaseDatabaseModel
from src.equipment_category.schemas import EquipmentCategory
from src.equipment_model.schemas import EquipmentModel
from src.institution.schemas import Institution
from src.manufacturer.schemas import Manufacturer
from src.models import StringToDate


class SparePart(BaseDatabaseModel):
    __tablename__ = "spare_part"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column()
    serial_number: Mapped[str | None] = mapped_column(nullable=True)

    supplier_id: Mapped[int] = mapped_column(ForeignKey("supplier.id"))
    supplier: Mapped["Supplier"] = relationship(back_populates="spare_parts")


