from src.equipment_category.models import EquipmentCategoryInfo
from src.equipment_category.schemas import EquipmentCategory
from src.repository import CRUDRepository
from src.services import GenericServices


class EquipmentCategoryServices(GenericServices[EquipmentCategory, EquipmentCategoryInfo]):
    def __init__(self):
        super().__init__(CRUDRepository(EquipmentCategory), EquipmentCategoryInfo)
