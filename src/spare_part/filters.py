from sqlalchemy import func
from sqlalchemy.orm import aliased

from src.filter import apply_filters, ModelType
from src.spare_part.models import SparePartState


def spare_part_filter(stmt, model: ModelType, filters: dict):
    stmt = apply_filters(stmt, model, filters)
    if "stock_state" in filters:
        loc = aliased(model.locations.property.mapper.class_)
        total_quantity = func.coalesce(func.sum(loc.quantity), 0)

        stmt = stmt.join(loc, model.locations, isouter=True).group_by(model.id)

        if filters["stock_state"] == SparePartState.InStock.value:
            stmt = stmt.having(total_quantity > model.min_quantity)
        elif filters["stock_state"] == SparePartState.OutOfStock.value:
            stmt = stmt.having(total_quantity == 0)
        elif filters["stock_state"] == SparePartState.LowStock.value:
            stmt = stmt.having(total_quantity <= model.min_quantity)

    return stmt
