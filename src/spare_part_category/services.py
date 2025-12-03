from src.repository import CRUDRepository
from src.services import GenericServices
from src.spare_part_category.models import SparePartCategoryInfo
from src.spare_part_category.schemas import SparePartCategory


class SparePartCategoryServices(GenericServices[SparePartCategory, SparePartCategoryInfo]):
    def __init__(self):
        super().__init__(CRUDRepository(SparePartCategory), SparePartCategoryInfo)