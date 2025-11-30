from typing import Callable

from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.schemas import User
from src.repository import CRUDRepository
from src.services import GenericServices
from src.smtp import LowStockMessagePayload
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
            send_low_stock_message_callback: Callable[[str, LowStockMessagePayload], None] | None = None,
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
            preloads=preloads)
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
        if quantity <= spare_part.min_quantity and send_low_stock_message_callback:
            receivers = await self.auth_repo.get(
                database=database,
                filters={"receive_low_stock_notification": True}
            )
            for receiver in receivers:
                send_low_stock_message_callback(receiver.email, LowStockMessagePayload(
                    receiver_username=receiver.username,
                    spare_part_name=spare_part.name,
                    spare_part_serial_number=spare_part.serial_number,
                    spare_part_current_quantity=quantity,
                    spare_part_min_quantity=spare_part.min_quantity,
                ))

        return SparePartInfo.model_validate(spare_part, from_attributes=True)
