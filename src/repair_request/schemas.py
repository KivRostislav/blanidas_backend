from datetime import datetime
from enum import Enum

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, relationship, mapped_column

from src.database import BaseDatabaseModel
from src.failure_type.schemas import FailureType, FailureTypeRepairRequest


class RepairRequestStatus(str, Enum):
    in_progress = "in_progress"
    not_taken = "not_taken"
    waiting_spare_parts = "waiting_spare_parts"
    finished = "finished"

class SparePartRepairRequest(BaseDatabaseModel):
    __tablename__ = "spare_part_repair_request"

    spare_part_id: Mapped[int] = mapped_column(ForeignKey("spare_part.id"), primary_key=True)
    repair_request_id: Mapped[int] = mapped_column(ForeignKey("repair_request.id"), primary_key=True)

class UrgencyLevel(str, Enum):
    critical = "critical"
    non_critical = "non_critical"

class RepairRequestState(BaseDatabaseModel):
    __tablename__ = "repair_request_state"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column()
    status: Mapped[RepairRequestStatus] = mapped_column()

    responsible_user_id: Mapped[int | None] = mapped_column(ForeignKey("user.id"), nullable=True)
    responsible_user: Mapped["User"] = relationship(back_populates="repair_request_states", lazy="noload")

    repair_request_id: Mapped[int | None] = mapped_column(ForeignKey("repair_request.id"), nullable=True)
    repair_request: Mapped["RepairRequest"] = relationship(back_populates="state_history", lazy="noload")

class File(BaseDatabaseModel):
    __tablename__ = "file"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    file_path: Mapped[str] = mapped_column()

    repair_request_id: Mapped[int] = mapped_column(ForeignKey("repair_request.id"))
    repair_request: Mapped["RepairRequest"] = relationship(back_populates="photos", lazy="noload")

class RepairRequest(BaseDatabaseModel):
    __tablename__ = "repair_request"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    description: Mapped[str] = mapped_column()
    urgency_level: Mapped[UrgencyLevel] = mapped_column()

    manager_note: Mapped[str] = mapped_column()
    engineer_note: Mapped[str] = mapped_column()

    used_spare_parts: Mapped[list["SparePart"]] = relationship(
        back_populates="repair_requests",
        secondary=SparePartRepairRequest.__table__,
        lazy="noload"
    )

    failure_types: Mapped[list["FailureType"]] = relationship(
        back_populates="repair_requests",
        secondary=FailureTypeRepairRequest.__table__,
        lazy="noload"
    )

    photos: Mapped[list["File"]] = relationship(
        back_populates="repair_request",
        cascade="all, delete",
        lazy="noload"
    )
    state_history: Mapped[list["RepairRequestState"]] = relationship(
        back_populates="repair_request",
        cascade="all, delete",
        lazy="noload"
    )

    equipment_id: Mapped[int | None] = mapped_column(ForeignKey("equipment.id"), nullable=True)
    equipment: Mapped["Equipment"] = relationship(back_populates="repair_requests", lazy="noload")
