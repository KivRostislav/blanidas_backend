from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import aliased

from src.auth.schemas import User, Role
from src.equipment.schemas import Equipment
from src.institution.schemas import Institution
from src.repair_request.schemas import RepairRequestStatus, RepairRequestState, RepairRequest
from src.spare_part.schemas import SparePart, SparePartLocationQuantity
from src.summary.models import UserSummary, InstitutionSummary, EquipmentSummary, SparePartSummary, RepairRequestSummary


user_rules = {
    "total": lambda db: db.scalar(select(func.count()).select_from(User)),
    "engineers": lambda db: db.scalar(select(func.count()).select_from(User).where(User.role == Role.engineer.value)),
    "managers": lambda db: db.scalar(select(func.count()).select_from(User).where(User.role == Role.manager.value)),
}


institution_rules = {
    "total": lambda db: db.scalar(select(func.count()).select_from(Institution)),
    "equipment": lambda db: db.scalar(select(func.count()).select_from(Equipment)),
    "users": lambda db: db.scalar(select(func.count()).select_from(User)),
}


rr = aliased(RepairRequest)
rrs = aliased(RepairRequestState)
row_number = func.row_number().over(
    partition_by=Equipment.id,
    order_by=rrs.created_at.desc()
).label("rn")

equipment_subquery = (
    select(Equipment, rr, rrs, row_number)
    .outerjoin(rr, Equipment.id == rr.equipment_id)
    .outerjoin(rrs, rr.id == rrs.repair_request_id)
).subquery()

equipment_rules = {
    "total": lambda db: db.scalar(select(func.count()).select_from(Equipment)),
    "working": lambda db: db.scalar(
        select(
            func.count()).select_from(equipment_subquery).where(
            and_(
                equipment_subquery.c.rn == 1,
                or_(
                    equipment_subquery.c.status == RepairRequestStatus.finished.value,
                    equipment_subquery.c.status.is_(None)
                )
            )
        )
    ),
    "under_maintenance": lambda db: db.scalar(
        select(
            func.count()).select_from(equipment_subquery).where(
            and_(
                equipment_subquery.c.rn == 1,
                equipment_subquery.c.status == RepairRequestStatus.in_progress.value
            )
        )
    ),
    "not_working": lambda db: db.scalar(
        select(
            func.count()).select_from(equipment_subquery).where(
            and_(
                equipment_subquery.c.rn == 1,
                or_(
                    equipment_subquery.c.status == RepairRequestStatus.not_taken.value,
                    equipment_subquery.c.status == RepairRequestStatus.waiting_spare_parts.value
                )
            )
        )
    ),
}


lq = aliased(SparePartLocationQuantity)
def build_quantity_subquery(having_condition):
    return (
        select(SparePart.id)
        .outerjoin(lq, SparePart.id == lq.spare_part_id)
        .group_by(SparePart.id)
        .having(having_condition)
        .subquery()
    )

in_stock_subquery = build_quantity_subquery(func.coalesce(func.sum(lq.quantity), 0) > SparePart.min_quantity)
low_stock_subquery = build_quantity_subquery(func.coalesce(func.sum(lq.quantity), 0) < SparePart.min_quantity)
out_of_stock_subquery = build_quantity_subquery(func.coalesce(func.sum(lq.quantity), 0) == 0)
spare_part_rules = {
    "total": lambda db: db.scalar(select(func.count()).select_from(SparePart)),
    "in_stock": lambda db: db.scalar(select(func.count()).select_from(in_stock_subquery)),
    "low_stock": lambda db: db.scalar(select(func.count()).select_from(low_stock_subquery)),
    "out_of_stock": lambda db: db.scalar(select(func.count()).select_from(out_of_stock_subquery)),
}


acs_row_number_col = func.row_number().over(
    partition_by=RepairRequest.id,
    order_by=RepairRequestState.created_at.asc()
).label("row_num")

acs_ranked_subquery = (
    select(
        RepairRequest,
        RepairRequestState,
        acs_row_number_col
    )
    .join(
        RepairRequestState,
        RepairRequest.id == RepairRequestState.repair_request_id,
        isouter=True
    )
    .cte("ranked_requests_asc")
)

desc_row_number_col = func.row_number().over(
    partition_by=RepairRequest.id,
    order_by=RepairRequestState.created_at.desc()
).label("row_num")

desc_ranked_subquery = (
    select(
        RepairRequest,
        RepairRequestState,
        desc_row_number_col
    )
    .join(
        RepairRequestState,
        RepairRequest.id == RepairRequestState.repair_request_id,
        isouter=True
    )
    .cte("ranked_requests_desc")
)

repair_part_rules = {
    "new": lambda db: db.scalar(
        select(func.count())
        .select_from(acs_ranked_subquery)
        .where(acs_ranked_subquery.c.row_num == 1)
    ),
    "in_progress": lambda db: db.scalar(
        select(func.count())
        .select_from(desc_ranked_subquery)
        .where(
            and_(
                desc_ranked_subquery.c.row_num == 1,
                desc_ranked_subquery.c.status == RepairRequestStatus.in_progress.value
            )
        )
    ),
    "waiting_spare_parts": lambda db: db.scalar(
        select(func.count())
        .select_from(desc_ranked_subquery)
        .where(
            and_(
                desc_ranked_subquery.c.row_num == 1,
                desc_ranked_subquery.c.status == RepairRequestStatus.waiting_spare_parts.value
            )
        )
    ),
    "finished": lambda db: db.scalar(
        select(func.count())
        .select_from(desc_ranked_subquery)
        .where(
            and_(
                desc_ranked_subquery.c.row_num == 1,
                desc_ranked_subquery.c.status == RepairRequestStatus.finished.value
            )
        )
    )
}


SUMMARY_RULES = {
    "repair_request": {
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
    "user": {
        "response_model": UserSummary,
        "rules": user_rules,
    },
    "institution": {
        "response_model": InstitutionSummary,
        "rules": institution_rules,
    },
}
