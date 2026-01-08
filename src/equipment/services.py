from src.equipment.models import EquipmentInfo
from src.equipment.repository import EquipmentRepository
from src.equipment.schemas import Equipment
from src.services import GenericServices

class EquipmentServices(GenericServices[Equipment, EquipmentInfo]):
    def __init__(self):
        super().__init__(EquipmentRepository(), EquipmentInfo)