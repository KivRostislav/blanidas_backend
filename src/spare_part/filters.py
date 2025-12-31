from sqlalchemy import func, select, case
from sqlalchemy.orm import aliased

from src.equipment_model.schemas import EquipmentModel
from src.filter import apply_filters, ModelType
from src.spare_part.models import SparePartState
from src.spare_part.schemas import SparePart, SparePartLocationQuantity


def apply_spare_parts_filters(stmt, model: ModelType, filters: dict):
    stmt = apply_filters(stmt, model, filters)
    if "stock_status__eq" in filters:
        locations = aliased(model.locations.property.mapper.class_)

        qty_subq = (
            select(
                locations.spare_part_id.label("spare_part_id"),
                func.sum(locations.quantity).label("total_quantity"),
            )
            .group_by(locations.spare_part_id)
            .subquery()
        )

        total_qty = func.coalesce(qty_subq.c.total_quantity, 0)

        stock_case = case(
            (total_qty == 0, "out_of_stock"),
            (total_qty <= model.min_quantity, "low_stock"),
            else_="in_stock",
        )

        stmt = (
            stmt
            .outerjoin(qty_subq, qty_subq.c.spare_part_id == model.id)
            .where(stock_case == filters["stock_status__eq"])
        )

    if "compatible_model_id__eq" in filters:
        stmt = stmt.where(SparePart.compatible_models.any(EquipmentModel.id == filters["compatible_model_id__eq"]))

    if "institution_id__eq" in filters:
        stmt = stmt.where(
            SparePart.locations.any(
                SparePartLocationQuantity.institution_id == filters["institution_id__eq"]
            )
        )

    return stmt
