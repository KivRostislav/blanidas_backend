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
        RRSR = aliased(RepairRequestStatusRecord)
        last_status_subquery = (
            select(
                RRSR.repair_request_id.label("rr_id"),
                RRSR.status.label("last_status"),
                func.row_number()
                .over(
                    partition_by=RRSR.repair_request_id,
                    order_by=RRSR.created_at.desc()
                )
                .label("rn")
            )
            .subquery()
        )

        status_order = case(
            (last_status_subquery.c.last_status == RepairRequestStatus.not_taken, 1),
            (last_status_subquery.c.last_status == RepairRequestStatus.in_progress, 2),
            (last_status_subquery.c.last_status == RepairRequestStatus.waiting_spare_parts, 3),
            (last_status_subquery.c.last_status == RepairRequestStatus.finished, 4),
        )

        if sorting.sort_order == SortOrder.descending:
            status_order = status_order.desc()

        stmt = (
            stmt
            .outerjoin(
                last_status_subquery,
                RepairRequest.id == last_status_subquery.c.rr_id
            )
            .where(
                or_(
                    last_status_subquery.c.rn == 1,
                    last_status_subquery.c.rn.is_(None)
                )
            )
            .order_by(status_order)
        )

    stmt = apply_sorting(stmt, sorting, related_fields)
    return stmt
