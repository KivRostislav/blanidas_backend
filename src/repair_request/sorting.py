from sqlalchemy import select, func, or_, case, Select
from sqlalchemy.orm import aliased

from src.equipment.schemas import Equipment
from src.equipment_model.schemas import EquipmentModel
from src.sorting import Sorting, SortingRelatedFieldsMap, SortOrder, apply_sorting
from src.repair_request.schemas import RepairRequest, RepairRequestStatusRecord, RepairRequestStatus


def apply_repair_request_sorting(stmt: Select, sorting: Sorting, related_fields: SortingRelatedFieldsMap) -> Select:
    if sorting.sort_by == "equipment_model_name":
        subq = (
            select(RepairRequest, EquipmentModel.name.label("model_name"))
            .join(Equipment, RepairRequest.equipment_id == Equipment.id)
            .join(EquipmentModel, Equipment.equipment_model_id == EquipmentModel.id)
            .subquery()
        )

        stmt = select(subq).order_by(
            subq.c.model_name.desc() if sorting.sort_order == SortOrder.descending else subq.c.model_name.asc()
        )

    if sorting.sort_by == "status":
        status_order = case(
            (RepairRequest.last_status == RepairRequestStatus.not_taken, 1),
            (RepairRequest.last_status == RepairRequestStatus.in_progress, 2),
            (RepairRequest.last_status == RepairRequestStatus.waiting_spare_parts, 3),
            (RepairRequest.last_status == RepairRequestStatus.finished, 4),
        )

        stmt = stmt.order_by(status_order.desc() if sorting.sort_order == SortOrder.descending else status_order.asc())

    stmt = apply_sorting(stmt, sorting, related_fields)
    return stmt
