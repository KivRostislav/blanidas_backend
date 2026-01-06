from sqlalchemy import select, func, and_, or_, case
from sqlalchemy.orm import aliased

from src.auth.schemas import User, Role
from src.equipment.schemas import Equipment
from src.institution.schemas import Institution
from src.repair_request.schemas import RepairRequestStatus, RepairRequestStatusRecord, RepairRequest
from src.spare_part.schemas import SparePart, Location
from src.summary.models import UserSummary, InstitutionSummary, EquipmentSummary, SparePartSummary, RepairRequestSummary

equipment_status_subq = (
    select(
        Equipment.id.label("equipment_id"),
        func.min(
            case(
                (RepairRequest.last_status == "not_taken", 1),
                (RepairRequest.last_status == "waiting_spare_parts", 2),
                (RepairRequest.last_status == "in_progress", 3),
                (RepairRequest.last_status == "finished", 4),
                else_=5
            )
        ).label("worst_status_priority")
    )
    .outerjoin(RepairRequest, RepairRequest.equipment_id == Equipment.id)
    .group_by(Equipment.id)
).subquery()

equipment_rules = {
    "total": lambda db: db.scalar(select(func.count()).select_from(Equipment)),
    "working": lambda db: db.scalar(
        select(func.count()).select_from(equipment_status_subq)
        .where(equipment_status_subq.c.worst_status_priority >= 4)
    ),
    "under_maintenance": lambda db: db.scalar(
        select(func.count()).select_from(equipment_status_subq)
        .where(equipment_status_subq.c.worst_status_priority == 3)
    ),
    "not_working": lambda db: db.scalar(
        select(func.count()).select_from(equipment_status_subq)
        .where(equipment_status_subq.c.worst_status_priority <= 2)
    ),
}
def quantity_subquery(condition):
    total_qty = func.coalesce(func.sum(Location.quantity), 0)
    return (
        select(SparePart.id)
        .outerjoin(Location, SparePart.id == Location.spare_part_id)
        .group_by(SparePart.id)
        .having(condition(total_qty))
        .subquery()
    )

spare_part_rules = {
    "total": lambda db: db.scalar(select(func.count()).select_from(SparePart)),
    "in_stock": lambda db: db.scalar(select(func.count()).select_from(quantity_subquery(lambda q: q > SparePart.min_quantity))),
    "low_stock": lambda db: db.scalar(select(func.count()).select_from(quantity_subquery(lambda q: q < SparePart.min_quantity))),
    "out_of_stock": lambda db: db.scalar(select(func.count()).select_from(quantity_subquery(lambda q: q == 0))),
}

repair_part_rules = {
    "new": lambda db: db.scalar(
        select(func.count())
        .select_from(RepairRequest)
        .where(RepairRequest.last_status == RepairRequestStatus.not_taken.value)
    ),
    "in_progress": lambda db: db.scalar(
        select(func.count())
        .select_from(RepairRequest)
        .where(RepairRequest.last_status == RepairRequestStatus.in_progress.value)
    ),
    "waiting_spare_parts": lambda db: db.scalar(
        select(func.count())
        .select_from(RepairRequest)
        .where(RepairRequest.last_status == RepairRequestStatus.waiting_spare_parts.value)
    ),
    "finished": lambda db: db.scalar(
        select(func.count())
        .select_from(RepairRequest)
        .where(RepairRequest.last_status == RepairRequestStatus.finished.value)
    )
}


SUMMARY_RULES = {
    "repair-requests": {
        "response_model": RepairRequestSummary,
        "rules": repair_part_rules,
    },
    "spare-parts": {
        "response_model": SparePartSummary,
        "rules": spare_part_rules,
    },
    "equipment": {
        "response_model": EquipmentSummary,
        "rules": equipment_rules,
    },
}
