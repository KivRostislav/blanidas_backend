from src.equipment.models import EquipmentInfo
from src.equipment.schemas import Equipment
from src.repository import CRUDRepository
from src.services import GenericServices


class EquipmentServices(GenericServices[Equipment, EquipmentInfo]):
    def __init__(self):
        super().__init__(CRUDRepository(Equipment), EquipmentInfo)