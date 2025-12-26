from datetime import datetime
from enum import Enum

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, relationship, mapped_column

from src.database import BaseDatabaseModel
from src.equipment.schemas import Equipment
from src.failure_type.schemas import FailureType, FailureTypeRepairRequest


class RepairRequestStatus(str, Enum):
    in_progress = "in_progress"
    not_taken = "not_taken"
    waiting_spare_parts = "waiting_spare_parts"
    finished = "finished"

class UrgencyLevel(str, Enum):
    critical = "critical"
    non_critical = "non_critical"

class RepairRequestState(BaseDatabaseModel):
    __tablename__ = "repair_request_state"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column()
    status: Mapped[RepairRequestStatus] = mapped_column()

    responsible_user_id: Mapped[int | None] = mapped_column(ForeignKey("user.id", ondelete="SET NULL"), nullable=True)
    responsible_user: Mapped["User"] = relationship(back_populates="repair_request_states", lazy="noload")

    repair_request_id: Mapped[int] = mapped_column(ForeignKey("repair_request.id", ondelete="CASCADE"))
    repair_request: Mapped["RepairRequest"] = relationship(back_populates="state_history", lazy="noload")

class File(BaseDatabaseModel):
    __tablename__ = "file"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    file_path: Mapped[str] = mapped_column()

    repair_request_id: Mapped[int] = mapped_column(ForeignKey("repair_request.id", ondelete="CASCADE"))
    repair_request: Mapped["RepairRequest"] = relationship(back_populates="photos", lazy="noload")

class RepairRequestUsedSparePart(BaseDatabaseModel):
    __tablename__ = "repair_request_used_spare_part"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    quantity: Mapped[int] = mapped_column()

    spare_part_id: Mapped[int | None] = mapped_column(ForeignKey("spare_part.id", ondelete="SET NULL"), nullable=True)
    spare_part: Mapped["SparePart"] = relationship(back_populates="repair_request_used_spare_parts", lazy="noload")

    institution_id: Mapped[int | None] = mapped_column(ForeignKey("institution.id", ondelete="SET NULL"), nullable=True)
    institution: Mapped["Institution"] = relationship(back_populates="repair_request_used_spare_parts", lazy="noload")

    repair_request_id: Mapped[int] = mapped_column(ForeignKey("repair_request.id", ondelete="CASCADE"))
    repair_request: Mapped["RepairRequest"] = relationship(back_populates="used_spare_parts", lazy="noload")


class RepairRequest(BaseDatabaseModel):
    __tablename__ = "repair_request"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    description: Mapped[str] = mapped_column()
    urgency_level: Mapped[UrgencyLevel] = mapped_column()
    created_at: Mapped[datetime] = mapped_column()
    completed_at: Mapped[datetime | None] = mapped_column(nullable=True)

    manager_note: Mapped[str | None] = mapped_column(nullable=True)
    engineer_note: Mapped[str | None] = mapped_column(nullable=True)

    used_spare_parts: Mapped[list["RepairRequestUsedSparePart"]] = relationship(
        back_populates="repair_request",
        cascade="all, delete-orphan",
        lazy="noload"
    )

    failure_types: Mapped[list["FailureType"]] = relationship(
        back_populates="repair_requests",
        secondary=FailureTypeRepairRequest.__table__,
        lazy="noload"
    )

    photos: Mapped[list["File"]] = relationship(
        back_populates="repair_request",
        cascade="all, delete-orphan",
        lazy="noload"
    )
    state_history: Mapped[list["RepairRequestState"]] = relationship(
        back_populates="repair_request",
        cascade="all, delete-orphan",
        lazy="noload"
    )

    equipment_id: Mapped[int | None] = mapped_column(ForeignKey("equipment.id", ondelete="SET NULL"), nullable=True)
    equipment: Mapped["Equipment"] = relationship(back_populates="repair_requests", lazy="noload")
