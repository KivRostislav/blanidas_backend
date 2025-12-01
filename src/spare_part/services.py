from fastapi import BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.schemas import User
from src.event import emit, EventTypes
from src.repository import CRUDRepository
from src.services import GenericServices
from src.mailer.smtp import MailerService
from src.mailer.models import LowStockMessagePayload
from src.spare_part.models import SparePartInfo
from src.spare_part.schemas import SparePart, SparePartLocationQuantity


class SparePartServices(GenericServices[SparePart, SparePartInfo]):
    def __init__(self):
        super().__init__(CRUDRepository(SparePart), SparePartInfo)
        self.spare_part_location_quantity_repo = CRUDRepository(SparePartLocationQuantity)
        self.auth_repo = CRUDRepository(User)

    async def create(
            self,
            data: dict,
            database: AsyncSession,
            unique_fields: list[str] | None = None,
            relationship_fields: list[str] | None = None,
            preloads: list[str] | None = None,
    ) -> SparePartInfo:
        locations_data = data["locations"]
        del data["locations"]
        spare_part = await super().create(
            data=data,
            database=database,
            unique_fields=unique_fields,
            relationship_fields=relationship_fields,
            preloads=preloads
        )
        for i in range(len(locations_data)):
            locations_data[i]["spare_part_id"] = spare_part.id
        locations = await self.spare_part_location_quantity_repo.create_many(
            data_list=locations_data,
            database=database,
            preloads=[
                "institution",
                "institution.institution_type"
            ]
        )
        spare_part.locations = locations
        return SparePartInfo.model_validate(spare_part, from_attributes=True)

    async def update(
            self,
            id: int,
            data: dict,
            database: AsyncSession,
            background_tasks: BackgroundTasks | None = None,
            mailer: MailerService | None = None,
            unique_fields: list[str] | None = None,
            relationship_fields: list[str] | None = None,
            preloads: list[str] | None = None,
    ) -> SparePartInfo:
        locations_data = data["locations"]
        del data["locations"]
        spare_part = await super().update(
            id=id,
            data=data,
            database=database,
            unique_fields=unique_fields,
            relationship_fields=relationship_fields,
            preloads=preloads
        )
        to_delete_ids = [x.id for x in spare_part.locations]
        await self.spare_part_location_quantity_repo.delete_many(ids=to_delete_ids, database=database)

        for i in range(len(locations_data)):
            locations_data[i]["spare_part_id"] = spare_part.id

        locations = await self.spare_part_location_quantity_repo.create_many(
            data_list=locations_data,
            database=database,
            preloads=[
                "institution",
                "institution.institution_type"
            ]
        )
        spare_part.locations = locations

        quantity = 0
        for location in locations_data:
            quantity += location["quantity"]
        if quantity <= spare_part.min_quantity and background_tasks and mailer:
            receivers = await self.auth_repo.get(
                database=database,
                filters={"receive_low_stock_notification": True}
            )
            for receiver in receivers:
                await emit(
                    event_name=EventTypes.low_stock.name,
                    background_tasks=background_tasks,
                    to=receiver.email,
                    mailer=mailer,
                    payload=LowStockMessagePayload(
                        receiver_username=receiver.username,
                        spare_part_name=spare_part.name,
                        spare_part_serial_number=spare_part.serial_number,
                        spare_part_current_quantity=quantity,
                        spare_part_min_quantity=spare_part.min_quantity,
                    )
                )
        return SparePartInfo.model_validate(spare_part.__dict__, from_attributes=True)
