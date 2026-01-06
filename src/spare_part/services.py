from statistics import quantiles
from typing import Any

from fastapi import BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.repository import AuthRepository
from src.auth.schemas import User
from src.equipment_model.schemas import EquipmentModel
from src.event import emit, EventTypes
from src.filters import FilterRelatedField, apply_filters_wrapper
from src.pagination import PaginationResponse, Pagination
from src.repository import CRUDRepository
from src.services import GenericServices
from src.mailer.smtp import MailerService
from src.mailer.models import LowStockMessagePayload
from src.spare_part.models import SparePartInfo
from src.spare_part.repository import SparePartRepository
from src.spare_part.schemas import SparePart


class SparePartServices(GenericServices[SparePart, SparePartInfo]):
    def __init__(self):
        super().__init__(SparePartRepository(), SparePartInfo)
        self.auth_repo = AuthRepository()

    async def update(
            self,
            id_: int,
            data: dict,
            database: AsyncSession,
            background_tasks: BackgroundTasks | None = None,
            mailer: MailerService | None = None,
            unique_fields: list[str] | None = None,
            relationship_fields: list[str] | None = None,
            overwrite_relationships: list[str] | None = None,
            preloads: list[str] | None = None,
    ) -> SparePartInfo:
        spare_part = await self.repo.update(id_=id_, data=data, database=database, preloads=preloads)

        quantity = 0
        for location in spare_part.locations:
            quantity += location.quantity
        if quantity <= spare_part.min_quantity and background_tasks and mailer:
            receivers = (await self.auth_repo.fetch(database=database, limit=-1, filters={"receive_low_stock_notification": "true"}))[0]
            for receiver in receivers:
                await emit(
                    event_name=EventTypes.low_stock.name,
                    background_tasks=background_tasks,
                    to=receiver.email,
                    mailer=mailer,
                    payload=LowStockMessagePayload(
                        receiver_username=receiver.username,
                        spare_part_name=spare_part.name,
                        spare_part_current_quantity=quantity,
                        spare_part_min_quantity=spare_part.min_quantity,
                    )
                )

        return SparePartInfo.model_validate({quantity: quantity, **spare_part.__dict__}, from_attributes=True)
