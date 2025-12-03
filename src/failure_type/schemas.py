from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, relationship, mapped_column

from src.database import BaseDatabaseModel


class FailureType(BaseDatabaseModel):
    __tablename__ = "failure_type"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column()

    repair_requests: Mapped[list["RepairRequest"]] = relationship(
        back_populates="failure_types",
        secondary="failure_type_repair_request",
        lazy="noload"
    )

class FailureTypeRepairRequest(BaseDatabaseModel):
    __tablename__ = "failure_type_repair_request"

    repair_request_id: Mapped[int] = mapped_column(ForeignKey("repair_request.id"), primary_key=True)
    failure_type_id: Mapped[int] = mapped_column(ForeignKey("failure_type.id"), primary_key=True)
