from src.equipment_model.models import EquipmentModelInfo
from src.equipment_model.schemas import EquipmentModel
from src.repository import CRUDRepository
from src.services import GenericServices


class EquipmentModelServices(GenericServices[EquipmentModel, EquipmentModelInfo]):
    def __init__(self):
        super().__init__(CRUDRepository(EquipmentModel), EquipmentModelInfo)