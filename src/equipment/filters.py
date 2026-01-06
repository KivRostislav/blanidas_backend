
from sqlalchemy import or_, select, Select, exists, not_, and_

from src.equipment.models import Status
from src.filters import Filters, FilterRelatedFieldsMap, get_filter_value
from src.equipment.schemas import Equipment
from src.equipment_model.schemas import EquipmentModel
from src.filters import apply_filters
from src.repair_request.schemas import RepairRequest, RepairRequestStatus


def apply_equipment_filters(stmt: Select, data: Filters, related_fields: FilterRelatedFieldsMap) -> Select:
    stmt = apply_filters(stmt, data, related_fields)

    or_conditions = get_filter_value(data.get("equipment_model_name_or_serial_number"), column=Equipment.serial_number)
    status = get_filter_value(data.get("status"), enum=Status)

    if or_conditions is not None:
        stmt = stmt.where(
            exists(
                select(1)
                .where(
                    and_(
                        EquipmentModel.id == Equipment.equipment_model_id,
                        or_(
                            Equipment.serial_number.ilike(f"%{or_conditions}%"),
                            EquipmentModel.name.ilike(f"%{or_conditions}%"),
                        )
                    )
                )
            )
        )
    if status is not None:
        rr = RepairRequest
        rrs = RepairRequestStatus
        if status == Status.working.value:
            condition = not_(exists(select(1).where(rr.equipment_id == Equipment.id, rr.last_status != rrs.finished,)))
        elif status == Status.under_maintenance.value:
            condition = exists(select(1).where(rr.equipment_id == Equipment.id, rr.last_status.in_([rrs.in_progress, rrs.waiting_spare_parts])))
        else:
            condition = exists(select(1).where(rr.equipment_id == Equipment.id, rr.last_status == rrs.not_taken))

        stmt = stmt.where(condition)

    return stmt
