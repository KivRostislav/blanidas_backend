from sqlalchemy import or_, select, func, and_, Select
from sqlalchemy.orm import aliased

from src.equipment.schemas import Equipment
from src.equipment_model.schemas import EquipmentModel
from src.filters import apply_filters, FilterRelatedFieldsMap, Filters, get_filter_value
from src.repair_request.schemas import RepairRequest


def apply_repair_request_filters(stmt: Select, filters: Filters, related_fields: FilterRelatedFieldsMap) -> Select:
    or_conditions = get_filter_value(filters.get("equipment_serial_number_or_equipment_equipment_model_name", None))
    equipment_category_id = get_filter_value(filters.get("equipment_category_id", None))
    equipment_institution_id = get_filter_value(filters.get("equipment_institution_id", None))

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

    equipment_alias = aliased(Equipment)
    if equipment_institution_id or equipment_category_id:
        stmt = stmt.join(equipment_alias, equipment_alias.id == RepairRequest.equipment_id)

    if equipment_institution_id:
        stmt = stmt.where(equipment_alias.institution_id == equipment_institution_id)

    if equipment_category_id:
        stmt = stmt.where(equipment_alias.equipment_category_id == equipment_category_id)

    return stmt
