from sqlalchemy import or_, func, select, case, literal
from sqlalchemy.orm import aliased

from src.equipment.schemas import Equipment
from src.equipment_model.schemas import EquipmentModel
from src.filter import apply_filters
from src.repair_request.schemas import RepairRequestStatusRecord, RepairRequest, RepairRequestStatus

SEVERITY = {
    RepairRequestStatus.finished: 0,
    RepairRequestStatus.in_progress: 1,
    RepairRequestStatus.waiting_spare_parts: 2,
    RepairRequestStatus.not_taken: 3,
}

SEVERITY_TO_LABEL = {
    0: "working",
    1: "under_maintenance",
    2: "under_maintenance",
    3: "not_working",
}

def apply_equipment_filters(stmt, model: Equipment, filters: dict):
    or_conditions = filters.pop("equipment_model__name__or__serial_number__ilike", None)
    status = filters.pop("status__eq", None)

    stmt = apply_filters(stmt, model, filters)
    if or_conditions is not None:
        stmt = (stmt
                .join(EquipmentModel, EquipmentModel.id == Equipment.equipment_model_id)
                .where(
                    or_(
                        Equipment.serial_number.ilike(f"%{or_conditions}%"),
                        EquipmentModel.name.ilike(f"%{or_conditions}%"),
                    )
        ))

    if status is not None:
        severity_expr = case(
            (RepairRequest.last_status == RepairRequestStatus.not_taken, 3),
            (RepairRequest.last_status == RepairRequestStatus.waiting_spare_parts, 2),
            (RepairRequest.last_status == RepairRequestStatus.in_progress, 1),
            (RepairRequest.last_status == RepairRequestStatus.finished, 0),
            else_=0,
        )

        max_severity = func.coalesce(func.max(severity_expr), literal(0))

        if status.value == "working":
            having_clause = max_severity == 0

        elif status.value == "under_maintenance":
            having_clause = max_severity.in_([1, 2])

        elif status.value == "not_working":
            having_clause = max_severity == 3

        stmt = (
            stmt
            .outerjoin(RepairRequest, RepairRequest.equipment_id == Equipment.id)
            .group_by(Equipment.id)
            .having(having_clause)
        )

    return stmt
