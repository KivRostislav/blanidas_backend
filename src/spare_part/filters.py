from sqlalchemy import func, select
from sqlalchemy.orm import aliased

from src.filter import apply_filters, ModelType
from src.spare_part.models import SparePartState


def spare_part_filter(stmt, model: ModelType, filters: dict):
    stmt = apply_filters(stmt, model, filters)
    if "stock_state" in filters:
        loc = aliased(model.locations.property.mapper.class_)
        qty_subq = (
            select(
                loc.spare_part_id.label("spare_part_id"),
                func.coalesce(func.sum(loc.quantity), 0).label("total_quantity"),
            )
            .group_by(loc.spare_part_id)
            .subquery()
        )

        stmt = stmt.outerjoin(qty_subq, qty_subq.c.spare_part_id == model.id)
        total_qty_col = func.coalesce(qty_subq.c.total_quantity, 0)

        state = filters["stock_state"]
        if state == SparePartState.InStock.value:
            stmt = stmt.where(total_qty_col > model.min_quantity)
        elif state == SparePartState.OutOfStock.value:
            stmt = stmt.where(total_qty_col == 0)
        elif state == SparePartState.LowStock.value:
            stmt = stmt.where(total_qty_col <= model.min_quantity)

    return stmt
