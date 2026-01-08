from math import ceil

from sqlalchemy import select, inspect, func, update, delete, insert, distinct
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, contains_eager, selectinload

from src.decorators import integrity_errors
from src.institution.models import InstitutionInfo
from src.sorting import Sorting, SortOrder, apply_sorting_wrapper, SortingRelatedField
from src.exceptions import DomainError, DomainErrorCode
from src.institution.schemas import Institution
from src.repository import CRUDRepository
from src.spare_part.filters import apply_spare_parts_filters
from src.spare_part.models import SparePartCreate, SparePartUpdate
from src.spare_part.schemas import SparePart, EquipmentModelSparePart, Location
from src.spare_part.sorting import apply_spare_parts_sorting
from src.utils import build_relation
from src.filters import Filters, apply_filters_wrapper, FilterRelatedField

filter_related_fields_map = {
    "name": FilterRelatedField(join=None, column=SparePart.name, use_exists=False),
    "spare_part_category_id": FilterRelatedField(join=None, column=SparePart.spare_part_category_id, use_exists=False),
    "compatible_model_id": None,
    "institution_id": None,
    "stock_status": None,
}

sorting_related_fields_map = {
    "name": SortingRelatedField(join=None, column=SparePart.name),
    "quantity": None,
    "stock_status": None,
}

class SparePartRepository(CRUDRepository[SparePart]):
    def __init__(self):
        super().__init__(
            SparePart,
            filter_callback=apply_filters_wrapper(apply_spare_parts_filters, filter_related_fields_map),
            sorting_callback=apply_sorting_wrapper(apply_spare_parts_sorting, sorting_related_fields_map),
        )

    @integrity_errors()
    async def create(self, data: dict, database: AsyncSession, preloads: list[str] | None = None) -> SparePart:
        data_model = SparePartCreate.model_validate(data)
        del data["compatible_models_ids"]

        row_id = (await database.execute(insert(SparePart).values(data).returning(SparePart.id))).scalar()

        for compatible_model_id in data_model.compatible_models_ids:
            await database.execute(insert(EquipmentModelSparePart).values({
                "equipment_model_id": compatible_model_id,
                "spare_part_id": row_id,
            }))

        await database.commit()

        options = build_relation(SparePart, preloads)
        stmt = select(SparePart).options(*options).where(SparePart.id == row_id)
        result = await database.execute(stmt)
        return result.scalars().first()

    @integrity_errors()
    async def update(self, id_: int, data: dict, database: AsyncSession, preloads: list[str] | None = None) -> SparePart:
        data_model = SparePartUpdate.model_validate(data)

        fields_to_update = data_model.model_dump(exclude={"locations", "compatible_models_ids"}, exclude_unset=True)
        rows = await database.execute(update(SparePart).where(SparePart.id == id_).values(fields_to_update))
        if rows.rowcount == 0:
            raise DomainError(DomainErrorCode.not_entity)

        if data_model.compatible_models_ids is not None:
            await database.execute(delete(EquipmentModelSparePart).where(EquipmentModelSparePart.spare_part_id == id_))
            for compatible_model_id in data_model.compatible_models_ids:
                await database.execute(insert(EquipmentModelSparePart).values({
                    "equipment_model_id": compatible_model_id,
                    "spare_part_id": id_,
                }))

        if data_model.locations is not None:
            await database.execute(delete(Location).where(Location.spare_part_id == id_))
            for location in data_model.locations:
                await database.execute(insert(Location).values({
                    "quantity": location.quantity,
                    "institution_id": location.institution_id,
                    "spare_part_id": id_,
                }))

        await database.commit()

        stmt = (
            select(SparePart)
            .join(SparePart.supplier, isouter=True)
            .join(SparePart.spare_part_category, isouter=True)
            .join(SparePart.manufacturer, isouter=True)
            .join(SparePart.compatible_models, isouter=True)
            .join(SparePart.locations, isouter=True)
            .join(Location.institution, isouter=True)
            .join(Institution.institution_type, isouter=True)
            .options(
                contains_eager(SparePart.supplier),
                contains_eager(SparePart.spare_part_category),
                contains_eager(SparePart.manufacturer),
                contains_eager(SparePart.compatible_models),
                contains_eager(SparePart.locations)
                .contains_eager(Location.institution)
                .contains_eager(Institution.institution_type),
            )

            .order_by(Institution.name)
            .where(SparePart.id == id_)
        )
        result = await database.execute(stmt)
        return result.scalars().first()


