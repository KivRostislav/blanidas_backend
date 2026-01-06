from src.equipment_category.models import EquipmentCategoryInfo
from src.equipment_category.schemas import EquipmentCategory
from src.filters import FilterRelatedField, apply_filters_wrapper, apply_filters
from src.repository import CRUDRepository
from src.services import GenericServices
from src.sorting import SortingRelatedField, apply_sorting_wrapper, apply_sorting

filter_related_fields_map = {"name": FilterRelatedField(join=None, column=EquipmentCategory.name, use_exists=False)}
sorting_related_fields_map = {"name": SortingRelatedField(join=None, column=EquipmentCategory.name)}

class EquipmentCategoryServices(GenericServices[EquipmentCategory, EquipmentCategoryInfo]):
    def __init__(self):
        super().__init__(CRUDRepository(
            EquipmentCategory,
            filter_callback=apply_filters_wrapper(apply_filters, filter_related_fields_map),
            sorting_callback=apply_sorting_wrapper(apply_sorting, sorting_related_fields_map)
        ), EquipmentCategoryInfo)
