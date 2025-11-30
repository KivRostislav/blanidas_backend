from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.repository import CRUDRepository
from src.spare_part.models import SparePartLocationQuantityInfo
from src.spare_part.schemas import SparePartLocationQuantity
from src.utils import validate_relationships


class SparePartLocationQuantityRepository(CRUDRepository[SparePartLocationQuantity]):
    async def create_all(
            self,
            data: list[dict],
            database: AsyncSession,
            relationship_fields: list[str] | None = None,
            preloads: list[str] | None = None,
    ) -> list[SparePartLocationQuantityInfo]:
        relationship_fields = relationship_fields if relationship_fields else []
        preloads = preloads if preloads else []

        if not await validate_relationships(self.model, data, database, relationship_fields):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Some foreign keys does not exist"
            )

        obj = self.model(**data)
        for field in many_to_many:
            rel = self.model.__mapper__.relationships[field]
            rel_model = rel.mapper.class_

            ids = data[field + "_ids"]
            result = await database.execute(select(rel_model).where(rel_model.id.in_(ids)))
            related_objs = result.scalars().all()
            getattr(obj, field).extend(related_objs)

        database.add(obj)
        await database.commit()

        preload_options = build_relation(self.model, preloads)
        stmt = select(self.model).options(*preload_options).where(self.model.id == obj.id)
        result = await database.execute(stmt)
        return result.scalars().first()
