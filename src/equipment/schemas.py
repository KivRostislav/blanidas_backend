from datetime import date
from enum import Enum

from sqlalchemy import ForeignKey, case, func, select, DateTime
from sqlalchemy.orm import Mapped, relationship, mapped_column, column_property

from src.database import BaseDatabaseModel
from src.repair_request.schemas import RepairRequest, RepairRequestStatus

class EquipmentStatus(str, Enum):
    working = 'working'
    under_maintenance = 'under_maintenance'
    not_working = 'not_working'

worst_status_case = func.max(
    case(
        (RepairRequest.last_status == RepairRequestStatus.not_taken, 2),
        (RepairRequest.last_status.in_([RepairRequestStatus.in_progress, RepairRequestStatus.waiting_spare_parts,]), 1),
        else_=0
    )
)

class Equipment(BaseDatabaseModel):
    __tablename__ = "equipment"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    location: Mapped[str] = mapped_column()
    serial_number: Mapped[str] = mapped_column(unique=True)
    installed: Mapped[date] = mapped_column(DateTime(timezone=True))

    status: Mapped[EquipmentStatus] = column_property(
        select(
            case(
                (worst_status_case == 2, EquipmentStatus.not_working),
                (worst_status_case == 1, EquipmentStatus.under_maintenance),
                else_=EquipmentStatus.working
            )
        )
        .where(RepairRequest.equipment_id == id)
        .correlate_except(RepairRequest)
        .scalar_subquery()
    )

    institution_id: Mapped[int] = mapped_column(ForeignKey("institution.id", ondelete="CASCADE"))
    institution: Mapped["Institution"] = relationship(back_populates="equipment", lazy="noload")

    equipment_model_id: Mapped[int] = mapped_column(ForeignKey("equipment_model.id", ondelete="CASCADE"), nullable=True)
    equipment_model: Mapped["EquipmentModel"] = relationship(back_populates="equipment", lazy="noload")

    equipment_category_id: Mapped[int | None] = mapped_column(ForeignKey("equipment_category.id", ondelete="SET NULL"), nullable=True)
    equipment_category: Mapped["EquipmentCategory"] = relationship(back_populates="equipment", lazy="noload")

    manufacturer_id: Mapped[int | None] = mapped_column(ForeignKey("manufacturer.id", ondelete="SET NULL"), nullable=True)
    manufacturer: Mapped["Manufacturer"] = relationship(back_populates="equipment", lazy="noload")

    repair_requests: Mapped[list["RepairRequest"]] = relationship(back_populates="equipment", lazy="noload")

