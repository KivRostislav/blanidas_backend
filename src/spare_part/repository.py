from math import ceil

from sqlalchemy import select, inspect, func
from sqlalchemy.exc import NoForeignKeysError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload, contains_eager

from sorting import Sorting, SortOrder
from src.equipment_model.schemas import EquipmentModel
from src.exceptions import NotFoundError
from src.institution.schemas import Institution
from src.pagination import Pagination
from src.repository import CRUDRepository
from src.spare_part.models import SparePartCreate, SparePartUpdate
from src.spare_part.schemas import SparePart, SparePartLocationQuantity
from src.spare_part.sorting import apply_spare_parts_sorting
from src.utils import validate_relationships, build_relation


class SparePartRepository(CRUDRepository[SparePart]):
    def __init__(self):
        super().__init__(SparePart, sorting_callback=apply_spare_parts_sorting)

    async def paginate(
            self,
            database: AsyncSession,
            pagination: Pagination,
            filters: dict | None = None,
            preloads: list[str] | None = None,
            sorting: Sorting | None = None,
    ) -> dict:
        preloads_mapper = inspect(SparePart).relationships.items()
        preloads_mapper.remove(list(filter(lambda x: x[0] == "locations", preloads_mapper))[0])
        filters = filters if filters else {}

        stmt = select(self.model)
        stmt = self.filter_callback(stmt, self.model, filters)

        if sorting:
            stmt = self.sorting_callback(stmt, self.model, sorting.order_by, sorting.order == SortOrder.descending)

        if preloads:
            options = build_relation(self.model, [x[0] for x in preloads_mapper])
            stmt = stmt.options(*options)

        stmt = (stmt.join(SparePart.locations, isouter=True)
            .join(SparePartLocationQuantity.institution, isouter=True)
            .options(
                contains_eager(SparePart.locations)
                .contains_eager(SparePartLocationQuantity.institution)
            )
            .order_by(Institution.name)
        )

        count_stmt = select(func.count(self.model.id)).select_from(self.model)
        if filters:
            count_stmt = self.filter_callback(count_stmt, self.model, filters)

        total = (await database.execute(count_stmt)).scalar() or 0

        if pagination.limit >= 0:
            stmt = stmt.offset(pagination.offset).limit(pagination.limit)

        result = await database.execute(stmt)
        items = result.unique().scalars().all()

        total_pages = max(1, ceil(total / pagination.limit))
        return {
            "items": items,
            "total": total,
            "page": pagination.page,
            "pages": total_pages,
            "limit": pagination.limit,
            "has_next": pagination.page < total_pages,
            "has_prev": pagination.page > 1,
        }


    async def create(
            self,
            data: dict,
            database: AsyncSession,
            unique_fields: list[str] | None = None,
            relationship_fields: list[str] | None = None,
            preloads: list[str] | None = None,
    ) -> SparePart:
        relationship_fields = relationship_fields or []
        preloads = preloads or []
        data_model = SparePartCreate.model_validate(data)

        if not validate_relationships(SparePart, data, database, relationship_fields):
            raise NoForeignKeysError()

        del data["locations"]
        del data["compatible_models_ids"]

        spare_part_obj = SparePart(**data)
        stmt = select(EquipmentModel).where(EquipmentModel.id.in_(data_model.compatible_models_ids))
        compatible_model_objs = (await database.execute(stmt)).scalars().all()

        for compatible_model_obj in compatible_model_objs:
            spare_part_obj.compatible_models.append(compatible_model_obj)

        database.add(spare_part_obj)
        await database.flush()

        for location in data_model.locations:
            database.add(SparePartLocationQuantity(
                quantity=location.quantity,
                institution_id=location.institution_id,
                spare_part_id=spare_part_obj.id,
            ))

        await database.commit()

        options = build_relation(SparePart, preloads)
        stmt = (select(SparePart).options(*options)
                .where(SparePart.id == spare_part_obj.id)
                .execution_options(populate_existing=True))
        result = await database.execute(stmt)
        return result.scalars().first()

    async def update(
            self,
            id_: int,
            data: dict,
            database: AsyncSession,
            unique_fields: list[str] | None = None,
            relationship_fields: list[str] | None = None,
            overwrite_relationships: list[str] | None = None,
            preloads: list[str] | None = None,
    ) -> SparePart:
        relationship_fields = relationship_fields or []
        overwrite_relationships = overwrite_relationships or []
        preloads = preloads or []

        data_model = SparePartUpdate.model_validate(data)

        options = [
            joinedload(SparePart.compatible_models),
            joinedload(SparePart.locations)
        ]

        stmt = select(SparePart).options(*options).where(SparePart.id == id_)
        spare_part_obj = (await database.execute(stmt)).scalars().first()

        if not spare_part_obj:
            raise NotFoundError()

        if not validate_relationships(SparePart, data, database, relationship_fields):
            raise NoForeignKeysError()

        for field, value in data_model.model_dump(exclude={"locations", "compatible_models_ids"}, exclude_unset=True).items():
            setattr(spare_part_obj, field, value)

        if data_model.compatible_models_ids is not None:
            stmt = select(EquipmentModel).where(EquipmentModel.id.in_(data_model.compatible_models_ids))
            compatible_model_objs = (await database.execute(stmt)).scalars().all()
            spare_part_obj.compatible_models.clear()
            await database.flush()

            for compatible_model_obj in compatible_model_objs:
                spare_part_obj.compatible_models.append(compatible_model_obj)

        incoming_ids = {
            loc.institution_id
            for loc in data_model.locations
        }
        for location in spare_part_obj.locations:
            if location.institution_id not in incoming_ids:
                await database.delete(location)

        if "locations" in overwrite_relationships and data_model.locations is not None:
            existing_locations = {
                loc.institution_id: loc
                for loc in spare_part_obj.locations
            }

            for location in data_model.locations:
                existing = existing_locations.get(location.institution_id)

                if location.quantity <= 0:
                    if existing:
                        await database.delete(existing)
                    continue

                if existing:
                    existing.quantity = location.quantity
                else:
                    database.add(
                        SparePartLocationQuantity(
                            quantity=location.quantity,
                            institution_id=location.institution_id,
                            spare_part_id=spare_part_obj.id,
                        )
                    )

        await database.commit()

        options = build_relation(SparePart, preloads)
        stmt = (
            select(SparePart)
            .options(*options)
            .where(SparePart.id == spare_part_obj.id)
            .execution_options(populate_existing=True)
        )
        result = await database.execute(stmt)
        return result.scalars().first()


