from sqlalchemy import select
from sqlalchemy.exc import NoForeignKeysError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.equipment_model.schemas import EquipmentModel
from src.exceptions import NotFoundError
from src.repair_request.models import CreateRepairRequestUsedSpareParts
from src.repository import CRUDRepository
from src.spare_part.models import SparePartCreate, SparePartUpdate
from src.spare_part.schemas import SparePart, SparePartLocationQuantity
from src.spare_part_category.schemas import SparePartCategory
from src.utils import validate_relationships, build_relation


class SparePartRepository(CRUDRepository[SparePart]):
    def __init__(self):
        super().__init__(SparePart)

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


