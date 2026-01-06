from sqlalchemy import select, func, case, and_, Select
from sqlalchemy.orm import aliased

from src.sorting import Sorting, SortingRelatedFieldsMap, SortOrder, apply_sorting
from src.spare_part.schemas import SparePart, Location

from sqlalchemy import select, func, case
from sqlalchemy import func, case, and_
from sqlalchemy import func, case, and_
from sqlalchemy.orm import aliased
from sqlalchemy import select, func, case


from sqlalchemy import case, and_, func
def apply_spare_parts_sorting(stmt: Select, sorting: Sorting, related_fields: SortingRelatedFieldsMap) -> Select:
    # Підзапит для підрахунку загальної кількості деталей
    total_quantity_subq = (
        select(
            Location.spare_part_id.label("spare_part_id"),
            func.coalesce(func.sum(Location.quantity), 0).label("total_quantity")
        )
        .group_by(Location.spare_part_id)
        .subquery()
    )

    # Аліас для підзапиту
    total_qty_alias = aliased(total_quantity_subq)

    # Колонка для сортування
    total_qty_col = func.coalesce(total_qty_alias.c.total_quantity, 0)

    if sorting.sort_by == "quantity":
        # Приєднуємо підзапит і сортуємо
        return stmt.outerjoin(
            total_qty_alias,
            SparePart.id == total_qty_alias.c.spare_part_id
        ).order_by(
            total_qty_col.desc() if sorting.sort_order == SortOrder.descending else total_qty_col.asc()
        )


    if sorting.sort_by == "stock_status":
        # Статус: 0 - out_of_stock, 1 - low_stock, 2 - in_stock
        status_expr = case(
            (total_qty_col > SparePart.min_quantity, 2),
            (and_(total_qty_col > 0, total_qty_col <= SparePart.min_quantity), 1),
            else_=0
        )

        return (
            stmt
            .outerjoin(total_quantity_subq, SparePart.id == total_quantity_subq.c.spare_part_id)
            .order_by(status_expr.desc() if sorting.sort_order == SortOrder.descending else status_expr.asc())
        )

    return apply_sorting(stmt, sorting, related_fields)
