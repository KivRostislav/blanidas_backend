from sqlalchemy import select, func, case, and_
from src.spare_part.schemas import SparePart, SparePartLocationQuantity
from src.spare_part.models import SparePartsSortBy
from src.filter import sorting_apply


def apply_spare_parts_sorting(stmt, model: SparePart, order_by: str, desc: bool):
    total_quantity = func.coalesce(func.sum(SparePartLocationQuantity.quantity), 0)
    total_quantity_subq = (
        select(SparePartLocationQuantity.spare_part_id, total_quantity.label("total_quantity"))
        .group_by(SparePartLocationQuantity.spare_part_id)
        .subquery()
    )

    if order_by == SparePartsSortBy.quantity.value:
        return (
            stmt
            .outerjoin(total_quantity_subq, SparePart.id == total_quantity_subq.c.spare_part_id)
            .order_by(total_quantity_subq.c.total_quantity.desc() if desc else total_quantity_subq.c.total_quantity.asc())
        )

    if order_by == SparePartsSortBy.status.value:
        status = case(
            (total_quantity_subq.c.total_quantity > SparePart.min_quantity, 2),
            (and_(
                total_quantity_subq.c.total_quantity > 0,
                total_quantity_subq.c.total_quantity < SparePart.min_quantity
            ), 1),
            (total_quantity_subq.c.total_quantity == 0, 0),
        )

        status_subq = (select(SparePart.id.label("spare_part_id"), status.label("status"))
                       .outerjoin(total_quantity_subq, SparePart.id == total_quantity_subq.c.spare_part_id).subquery())

        return (
            stmt
            .outerjoin(status_subq, SparePart.id == status_subq.c.spare_part_id)
            .order_by(status_subq.c.status.desc() if desc else status_subq.c.status.asc())
        )



    return sorting_apply(stmt, model, order_by, desc)
