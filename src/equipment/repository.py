from sqlalchemy import select, func, distinct
from sqlalchemy.ext.asyncio import AsyncSession

from src.equipment.filters import apply_equipment_filters
from src.equipment.models import EquipmentStatus, EquipmentQrData
from src.equipment.schemas import Equipment
from src.equipment_model.schemas import EquipmentModel
from src.exceptions import DomainError, DomainErrorCode
from src.filters import apply_filters_wrapper, FilterRelatedField, Filters
from src.institution.schemas import Institution
from src.manufacturer.schemas import Manufacturer
from src.repository import CRUDRepository
from src.sorting import apply_sorting_wrapper, SortingRelatedField, apply_sorting, Sorting
from src.utils import build_relation

filter_related_fields_map = {
    "status": FilterRelatedField(join=None, column=Equipment.status, use_exists=False),
    "equipment_model_name_or_serial_number": None,
    "institution_id": FilterRelatedField(join=None, column=Equipment.institution_id, use_exists=False),
    "equipment_model_id": FilterRelatedField(join=None, column=Equipment.equipment_model_id, use_exists=False),
    "manufacturer_id": FilterRelatedField(join=None, column=Equipment.manufacturer_id, use_exists=False),
}

sorting_related_fields_map = {
    "name": SortingRelatedField(join=Equipment.equipment_model, column=EquipmentModel.name),
    "institution_name": SortingRelatedField(join=Equipment.institution, column=Institution.name),
    "manufacturer_name": SortingRelatedField(join=Equipment.manufacturer, column=Manufacturer.name),
}

class EquipmentRepository(CRUDRepository[Equipment]):
    def __init__(self):
        super().__init__(
            Equipment,
            filter_callback=apply_filters_wrapper(apply_equipment_filters, filter_related_fields_map),
            sorting_callback=apply_sorting_wrapper(apply_sorting, sorting_related_fields_map),
       )

    async def get(self, id_: int, database: AsyncSession, preloads: list[str] | None = None) -> Equipment:
        options = build_relation(Equipment, preloads or [])
        stmt = select(Equipment).options(*options).where(Equipment.id == id_)
        obj = (await database.execute(stmt)).unique().scalars().first()

        if obj is None:
            raise DomainError(code=DomainErrorCode.not_entity)

        return obj

    async def get_qr_data(self, database: AsyncSession) -> list[EquipmentQrData]:
        stmt = (select(Equipment.id, Equipment.serial_number, Institution.name.label("institution_name"))
                .join(Institution, Institution.id == Equipment.institution_id))
        rows = (await database.execute(stmt)).mappings().all()
        return [EquipmentQrData(**row) for row in rows]
