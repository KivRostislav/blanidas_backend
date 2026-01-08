from sqlalchemy import select, func, distinct
from sqlalchemy.ext.asyncio import AsyncSession

from src.equipment.filters import apply_equipment_filters
from src.equipment.models import EquipmentStatus
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

    async def fetch(
            self,
            database: AsyncSession,
            filters: Filters | None = None,
            preloads: list[str] | None = None,
            sorting: Sorting | None = None,
            offset: int | None = None,
            limit: int | None = None,
    ) -> tuple[list[Equipment], int]:
        filters = filters or {}
        preloads = preloads or []

        stmt = select(self.model)
        stmt = self.filter_callback(stmt, filters)

        if sorting:
            stmt = self.sorting_callback(stmt, sorting)

        if preloads:
            options = build_relation(self.model, preloads)
            stmt = stmt.options(*options)

        count_stmt = select(func.count(distinct(self.model.id))).select_from(self.model)
        if filters:
            count_stmt = self.filter_callback(count_stmt, filters)

        total = (await database.execute(count_stmt)).scalar() or 0

        if limit is not None and limit != -1:
            stmt = stmt.offset(offset or 0).limit(limit)

        result = await database.execute(stmt)
        items = result.unique().scalars().all()

        return list(items), total

    async def get(self, id_: int, database: AsyncSession, preloads: list[str] | None = None) -> Equipment:
        options = build_relation(Equipment, preloads or [])
        stmt = select(Equipment).options(*options).where(Equipment.id == id_)
        obj = (await database.execute(stmt)).unique().scalars().first()

        if obj is None:
            raise DomainError(code=DomainErrorCode.not_entity)

        return obj
