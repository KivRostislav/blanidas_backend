from sqlalchemy.ext.asyncio import AsyncSession

from src.equipment.models import EquipmentInfo, EquipmentQrData
from src.equipment.repository import EquipmentRepository
from src.equipment.schemas import Equipment
from src.services import GenericServices

class EquipmentServices(GenericServices[Equipment, EquipmentInfo]):
    def __init__(self):
        super().__init__(EquipmentRepository(), EquipmentInfo)
        self.repo = EquipmentRepository()

    async def get_qr_data(self, database: AsyncSession) -> list[EquipmentQrData]:
        return await self.repo.get_qr_data(database)