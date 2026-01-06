from src.filters import FilterRelatedField, apply_filters_wrapper, apply_filters
from src.repository import CRUDRepository
from src.services import GenericServices
from src.sorting import SortingRelatedField, apply_sorting_wrapper, apply_sorting
from src.spare_part_category.models import SparePartCategoryInfo
from src.spare_part_category.schemas import SparePartCategory

filter_related_fields_map = {"name": FilterRelatedField(join=None, column=SparePartCategory.name, use_exists=False)}
sorting_related_fields_map = {"name": SortingRelatedField(join=None, column=SparePartCategory.name)}

class SparePartCategoryServices(GenericServices[SparePartCategory, SparePartCategoryInfo]):
    def __init__(self):
        super().__init__(CRUDRepository(
            SparePartCategory,
            filter_callback = apply_filters_wrapper(apply_filters, filter_related_fields_map),
            sorting_callback = apply_sorting_wrapper(apply_sorting, sorting_related_fields_map),
        ), SparePartCategoryInfo)