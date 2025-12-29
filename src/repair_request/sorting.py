from sqlalchemy import select, func, or_, case
from sqlalchemy.orm import aliased

from src.filter import sorting_apply
from src.repair_request.models import RepairRequestSortBy
from src.repair_request.schemas import RepairRequest, RepairRequestStatusRecord, RepairRequestStatus


def apply_repair_request_sorting(stmt, model: RepairRequest, order_by: str, desc: bool):
    stmt = sorting_apply(stmt, model, order_by, desc)
    if order_by == RepairRequestSortBy.status.value:
        rrsr = aliased(RepairRequestStatusRecord)

        last_status_subq = (
            select(
                rrsr.repair_request_id.label("rr_id"),
                rrsr.status.label("last_status"),
                func.row_number()
                .over(
                    partition_by=rrsr.repair_request_id,
                    order_by=rrsr.created_at.desc()
                )
                .label("rn")
            )
            .subquery()
        )

        status_order = case(
            (last_status_subq.c.last_status == RepairRequestStatus.not_taken, 1),
            (last_status_subq.c.last_status == RepairRequestStatus.in_progress, 2),
            (last_status_subq.c.last_status == RepairRequestStatus.waiting_spare_parts, 3),
            (last_status_subq.c.last_status == RepairRequestStatus.finished, 4),
        )

        if desc:
            status_order = status_order.desc()

        stmt = (
            stmt
            .outerjoin(
                last_status_subq,
                RepairRequest.id == last_status_subq.c.rr_id
            )
            .where(
                or_(
                    last_status_subq.c.rn == 1,
                    last_status_subq.c.rn.is_(None)
                )
            )
            .order_by(status_order)
        )
    return stmt
