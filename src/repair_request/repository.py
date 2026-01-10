from datetime import datetime
from typing import Callable

from sqlalchemy import select, and_, update, delete, func
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.auth.schemas import User
from src.decorators import integrity_errors
from src.equipment.schemas import Equipment
from src.equipment_category.schemas import EquipmentCategory
from src.exceptions import DomainError, DomainErrorCode
from src.failure_type.schemas import FailureType, FailureTypeRepairRequest
from src.filters import FilterRelatedField, apply_filters_wrapper
from src.repair_request.filters import apply_repair_request_filters
from src.repair_request.models import RepairRequestUpdate
from src.repair_request.schemas import RepairRequest, RepairRequestStatus, File, RepairRequestStatusRecord, UsedSparePart
from src.repair_request.sorting import apply_repair_request_sorting
from src.repository import CRUDRepository
from src.sorting import SortingRelatedField, apply_sorting_wrapper
from src.spare_part.schemas import Location
from src.utils import build_relation


filter_related_fields_map = {
    "id": FilterRelatedField(column=RepairRequest.id),
    "status": FilterRelatedField(column=RepairRequest.last_status),
    "equipment_id": FilterRelatedField(column=RepairRequest.equipment_id),
    "urgency": FilterRelatedField(column=RepairRequest.urgency),

    "equipment_category_id": None,
    "equipment_institution_id": None,
    "equipment_serial_number_or_equipment_equipment_model_name": None,
}

sorting_related_fields_map = {
    "created_at": SortingRelatedField(column=RepairRequest.created_at),

    "urgency": None,
    "status": None,
    "equipment_model_name": None,
}

class RepairRequestRepository(CRUDRepository[RepairRequest]):
    def __init__(self):
        super().__init__(
            RepairRequest,
            filter_callback=apply_filters_wrapper(apply_repair_request_filters, filter_related_fields_map),
            sorting_callback=apply_sorting_wrapper(apply_repair_request_sorting, sorting_related_fields_map),
       )

    @integrity_errors()
    async def create(
            self,
            data: dict,
            database: AsyncSession,
            preloads: list[str] | None = None,
            validate_photos_callback: Callable[[], list[str]] | None = None,
    ) -> RepairRequest:

        row_id = (await database.execute(insert(RepairRequest).values(
            **data,
            manager_note="",
            engineer_note="",
            created_at=func.now(),
            last_status=RepairRequestStatus.not_taken
        ).returning(RepairRequest.id))).scalar()

        await database.execute(insert(RepairRequestStatusRecord).values(
            repair_request_id=row_id,
            status=RepairRequestStatus.not_taken,
            created_at=func.now(),
            assigned_engineer_id=None,
        ))

        if validate_photos_callback:
            new_filenames = validate_photos_callback()
            for new_filename in new_filenames:
                await database.execute(insert(File).values(repair_request_id=row_id, file_path=new_filename))

        await database.commit()

        options = build_relation(RepairRequest, preloads)
        stmt = (select(RepairRequest).options(*options).where(RepairRequest.id == row_id))
        result = await database.execute(stmt)
        return result.scalars().first()

    @integrity_errors()
    async def update(self, id_: int, data: dict, database: AsyncSession, preloads: list[str] | None = None) -> RepairRequest:
        data_model = RepairRequestUpdate.model_validate(data)

        fields_to_update = data_model.model_dump(exclude={"status_history", "used_spare_parts", "failure_types_ids"}, exclude_unset=True)
        result = await database.execute(
            update(RepairRequest)
            .where(RepairRequest.id == id_)
            .values(fields_to_update)
            .returning(RepairRequest.id)
        )

        if result.first() is None:
            raise DomainError(code=DomainErrorCode.not_entity)

        if data_model.failure_types_ids:
            await database.execute(delete(FailureTypeRepairRequest).where(FailureTypeRepairRequest.repair_request_id == id_))
            for failure_type_id in data_model.failure_types_ids:
                await database.execute(insert(FailureTypeRepairRequest).values(
                    repair_request_id=id_,
                    failure_type_id=failure_type_id,
                ))

        if data_model.status_history:
            await database.execute(insert(RepairRequestStatusRecord).values(
                repair_request_id=id_,
                created_at=func.now(),
                assigned_engineer_id=data_model.status_history.assigned_engineer_id,
                status=data_model.status_history.status,
            ))
            completed_at = func.now() if data_model.status_history.status == RepairRequestStatus.finished else None
            await database.execute(update(RepairRequest).where(RepairRequest.id == id_).values(
                last_status=data_model.status_history.status,
                completed_at=completed_at
            ))

        if data_model.used_spare_parts is not None:
            used_spare_parts = (await database.execute(select(UsedSparePart).where(UsedSparePart.repair_request_id == id_))).scalars().all()
            old_parts = {(usp.spare_part_id, usp.institution_id): usp for usp in used_spare_parts}
            new_parts = {(usp.spare_part_id, usp.institution_id): usp for usp in data_model.used_spare_parts}

            for key, old_usp in old_parts.items():
                spare_part_id, institution_id = key
                old_qty = old_usp.quantity
                new_qty = new_parts.get(key, None).quantity if key in new_parts else 0
                diff = old_qty - new_qty

                if diff > 0:
                    stmt = insert(Location).values(
                        spare_part_id=spare_part_id,
                        institution_id=institution_id,
                        quantity=diff
                    ).on_conflict_do_update(
                        index_elements=[
                            Location.spare_part_id,
                            Location.institution_id,
                        ],
                        set_={
                            "quantity": Location.quantity + diff,
                        }
                    )
                    await database.execute(stmt)


            for key, new_usp in new_parts.items():
                spare_part_id, institution_id = key
                old_qty = old_parts.get(key).quantity if key in old_parts else 0
                diff = new_usp.quantity - old_qty

                if diff > 0:
                    stmt = insert(Location).values(
                        spare_part_id=spare_part_id,
                        institution_id=institution_id,
                        quantity=diff
                    ).on_conflict_do_update(
                        index_elements=[
                            Location.spare_part_id,
                            Location.institution_id,
                        ],
                        set_={
                            "quantity": Location.quantity - diff,
                        }
                    ).returning(Location.id, Location.quantity)
                    row = (await database.execute(stmt)).first()
                    if row is not None and row.quantity == 0:
                        await database.execute(delete(Location).where(Location.id == row.id))

            await database.execute(delete(UsedSparePart).where(UsedSparePart.repair_request_id == id_))
            for usp in data_model.used_spare_parts:
                await database.execute(insert(UsedSparePart).values(
                    repair_request_id=id_,
                    spare_part_id=usp.spare_part_id,
                    institution_id=usp.institution_id,
                    quantity=usp.quantity,
                    note=usp.note,
                ))

        await database.commit()

        options = build_relation(RepairRequest, preloads)
        stmt = select(RepairRequest).options(*options).where(RepairRequest.id == id_)
        result = await database.execute(stmt)
        return result.scalars().first()

class FileRepository(CRUDRepository[File]):
    def __init__(self):
        super().__init__(File)

    async def get_by_repair_request_id(self, repair_request_id: int, database: AsyncSession) -> list[File]:
        stmt = select(File).where(File.repair_request_id == repair_request_id)
        return list((await database.execute(stmt)).unique().scalars().all())