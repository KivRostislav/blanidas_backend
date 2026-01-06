from sqlalchemy import or_, select, func, and_, Select
from sqlalchemy.orm import aliased

from src.equipment.schemas import Equipment
from src.equipment_model.schemas import EquipmentModel
from src.filters import apply_filters, FilterRelatedFieldsMap, Filters, get_filter_value
from src.repair_request.schemas import RepairRequest


def apply_repair_request_filters(stmt: Select, filters: Filters, related_fields: FilterRelatedFieldsMap) -> Select:
    or_conditions = get_filter_value(filters.pop("equipment_serial_number_or_equipment_equipment_model_name", None))

    stmt = apply_filters(stmt, filters, related_fields)
    if or_conditions:
        stmt = (
            stmt
            .join(Equipment, Equipment.id == RepairRequest.equipment_id)
            .join(EquipmentModel, EquipmentModel.id == Equipment.equipment_model_id)
            .where(
                or_(
                    Equipment.serial_number.ilike(f"%{or_conditions}%"),
                    EquipmentModel.name.ilike(f"%{or_conditions}%")
                )
            )
        )

    return stmt
