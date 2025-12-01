from datetime import datetime
from enum import Enum

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, relationship, mapped_column

from src.database import BaseDatabaseModel
from src.equipment.schemas import Equipment
from src.spare_part.schemas import SparePart

class SparePartRepairRequest(BaseDatabaseModel):
    __tablename__ = "spare_part_repair_request"

    spare_part_id: Mapped[int] = mapped_column(ForeignKey("spare_part.id"), primary_key=True)
    repair_request_id: Mapped[int] = mapped_column(ForeignKey("repair_request.id"), primary_key=True)


class UrgencyLevel(str, Enum):
    critical = "critical"
    non_critical = "non_critical"

class RepairRequest(BaseDatabaseModel):
    __tablename__ = "repair_request"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    description: Mapped[str] = mapped_column()

    urgency_level: Mapped[UrgencyLevel] = mapped_column()
    created_at: datetime = mapped_column()

    manager_note: Mapped[str] = mapped_column()
    engineer_note: Mapped[str] = mapped_column()

    used_spare_parts: Mapped[list["SparePart"]] = relationship(
        back_populates="repair_requests",
        secondary=SparePartRepairRequest.__table__,
    )

    equipment_id: Mapped[int | None] = mapped_column(ForeignKey("equipment.id"), nullable=True)
    equipment: Mapped["Equipment"] = relationship(back_populates="repair_requests", lazy="noload")
