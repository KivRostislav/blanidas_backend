from datetime import datetime
from math import ceil
from typing import Callable

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from sorting import Sorting
from src.auth.schemas import User
from src.exceptions import NotFoundError, ForeignKeyNotFoundError
from src.failure_type.schemas import FailureType
from src.pagination import Pagination
from src.repair_request.filters import apply_repair_request_filters
from src.repair_request.models import RepairRequestUpdate
from src.repair_request.schemas import RepairRequest, RepairRequestStatus, File, RepairRequestStatusRecord, \
    UsedSparePart
from src.repair_request.sorting import apply_repair_request_sorting
from src.repository import CRUDRepository
from src.spare_part.schemas import SparePartLocationQuantity
from src.utils import build_relation, validate_relationships


class RepairRequestRepository(CRUDRepository[RepairRequest]):
    def __init__(self):
        super().__init__(
            RepairRequest,
            apply_repair_request_filters,
            apply_repair_request_sorting,
        )

    async def create(
            self,
            data: dict,
            database: AsyncSession,
            unique_fields: list[str] | None = None,
            relationship_fields: list[str] | None = None,
            preloads: list[str] | None = None,
            validate_photos_callback: Callable[[], list[str]] | None = None,
    ) -> RepairRequest:
        if not validate_relationships(RepairRequest, data, database, ["equipment"]):
            raise ForeignKeyNotFoundError()

        data["created_at"] = datetime.now()
        repair_request_obj = RepairRequest(
            **data,
            manager_note="",
            engineer_note="",
        )

        database.add(repair_request_obj)
        await database.flush()

        status_history_obj = RepairRequestStatusRecord(
            repair_request_id=repair_request_obj.id,
            status=RepairRequestStatus.not_taken,
            created_at=datetime.now(),
            assigned_engineer=None,
        )
        database.add(status_history_obj)

        new_filenames = validate_photos_callback()
        file_objs = [File(
            repair_request_id=repair_request_obj.id,
            file_path=new_filename
        ) for new_filename in new_filenames]

        database.add_all(file_objs)
        await database.commit()

        options = build_relation(RepairRequest, preloads)
        stmt = (select(RepairRequest)
                .options(*options)
                .where(RepairRequest.id == repair_request_obj.id)
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
    ) -> RepairRequest:
        data_model = RepairRequestUpdate.model_validate(data)

        options = [
            joinedload(RepairRequest.status_history),
            joinedload(RepairRequest.failure_types),
            joinedload(RepairRequest.used_spare_parts)
        ]

        stmt = select(RepairRequest).options(*options).where(RepairRequest.id == id_)
        result = await database.execute(stmt)
        obj = result.scalars().first()

        if not obj:
            raise NotFoundError(self.model.__name__, id_)

        if not await validate_relationships(self.model, data, database, ["failure_types"]):
            raise ForeignKeyNotFoundError()

        for field, value in data_model.model_dump(exclude={"status_history", "used_spare_parts"}, exclude_unset=True).items():
            setattr(obj, field, value)

        if data_model.failure_types_ids is not None:
            failure_types = (await database.execute(
                select(FailureType).where(FailureType.id.in_(data_model.failure_types_ids))
            )).scalars().all()
            obj.failure_types.clear()
            await database.flush()
            obj.failure_types.extend(failure_types)

        if data_model.status_history:
            assigned_engineer_id = data_model.status_history.assigned_engineer_id
            if assigned_engineer_id:
                responsible_user = (await database.execute(
                    select(User).where(User.id == assigned_engineer_id)
                )).scalars().first()
                if not responsible_user:
                    raise ForeignKeyNotFoundError()
            status_history_obj = RepairRequestStatusRecord(
                repair_request_id=obj.id,
                created_at=datetime.now(),
                assigned_engineer_id=assigned_engineer_id,
                status=data_model.status_history.status,
            )
            database.add(status_history_obj)

            if data_model.status_history.status == RepairRequestStatus.finished:
                obj.completed_at = datetime.now()

        if data_model.used_spare_parts is not None:
            old_parts = {(usp.spare_part_id, usp.institution_id): usp for usp in obj.used_spare_parts}
            new_parts = {(usp.spare_part_id, usp.institution_id): usp for usp in data_model.used_spare_parts}

            for key, old_usp in old_parts.items():
                spare_part_id, institution_id = key
                old_qty = old_usp.quantity
                new_qty = new_parts.get(key, None).quantity if key in new_parts else 0
                diff = old_qty - new_qty

                if diff > 0:
                    location = (await database.execute(
                        select(SparePartLocationQuantity)
                        .where(
                            and_(
                                SparePartLocationQuantity.spare_part_id == old_usp.spare_part_id,
                                SparePartLocationQuantity.institution_id == old_usp.institution_id,
                            )
                        )
                    )).scalars().first()
                    if location:
                        location.quantity += diff
                    else:
                        location = SparePartLocationQuantity(
                            spare_part_id=spare_part_id,
                            institution_id=institution_id,
                            quantity=diff
                        )
                    database.add(location)

            for key, new_usp in new_parts.items():
                spare_part_id, institution_id = key
                old_qty = old_parts.get(key).quantity if key in old_parts else 0
                diff = new_usp.quantity - old_qty

                if diff > 0:
                    location = (await database.execute(
                        select(SparePartLocationQuantity)
                        .where(
                            and_(
                                SparePartLocationQuantity.spare_part_id == new_usp.spare_part_id,
                                SparePartLocationQuantity.institution_id == new_usp.institution_id,
                            )
                        )
                    )).scalars().first()
                    if not location:
                        location = SparePartLocationQuantity(
                            spare_part_id=spare_part_id,
                            institution_id=institution_id,
                            quantity=0
                        )
                    if location.quantity < diff:
                        raise ValueError(f"Not enough details of spare part {spare_part_id} in institution {institution_id}")
                    location.quantity -= diff
                    if location.quantity <= 0:
                        await database.delete(location)
                    else:
                        database.add(location)

            obj.used_spare_parts.clear()
            await database.flush()
            for usp in data_model.used_spare_parts:
                used_part = UsedSparePart(
                    repair_request_id=obj.id,
                    spare_part_id=usp.spare_part_id,
                    institution_id=usp.institution_id,
                    quantity=usp.quantity,
                    note=usp.note,
                )
                database.add(used_part)

        database.add(obj)
        await database.commit()
        await database.refresh(obj)

        if preloads:
            options = build_relation(RepairRequest, preloads)
            stmt = select(RepairRequest).options(*options).where(RepairRequest.id == obj.id)
            result = await database.execute(stmt)
            return result.scalars().first()

        return obj

