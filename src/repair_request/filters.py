from sqlalchemy import or_, select, func, and_
from sqlalchemy.orm import aliased

from src.equipment.schemas import Equipment
from src.equipment_model.schemas import EquipmentModel
from src.filter import apply_filters
from src.repair_request.schemas import RepairRequest, RepairRequestStatusRecord


def apply_repair_request_filters(stmt, model: RepairRequest, filters: dict):
    or_conditions = filters.pop("equipment__serial_number__or__equipment__equipment_model__name__ilike", None)
    status = filters.pop("status__eq", None)

    stmt = apply_filters(stmt, model, filters)
    if or_conditions is not None:
        stmt = (stmt
                .join(Equipment, Equipment.id == RepairRequest.equipment_id)
                .join(EquipmentModel, EquipmentModel.id == Equipment.equipment_model_id)
                .where(
            or_(
                Equipment.serial_number.ilike(f"%{or_conditions}%"),
                EquipmentModel.name.ilike(f"%{or_conditions}%"),
            )
        ))

    if status is not None:
        lastState = aliased(RepairRequestStatusRecord)

        last_state_subq = (
            select(
                RepairRequestStatusRecord.repair_request_id,
                func.max(RepairRequestStatusRecord.created_at).label("max_created_at")
            )
            .group_by(RepairRequestStatusRecord.repair_request_id)
            .subquery()
        )

        stmt = (
            stmt
            .join(
                last_state_subq,
                last_state_subq.c.repair_request_id == RepairRequest.id
            )
            .join(
                lastState,
                and_(
                    lastState.repair_request_id == RepairRequest.id,
                    lastState.created_at == last_state_subq.c.max_created_at,
                )
            )
            .where(lastState.status == status)
        )

    return stmt
