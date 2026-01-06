from src.filters import FilterRelatedField, apply_filters_wrapper, FilterRelatedFieldsMap, apply_filters
from src.manufacturer.models import ManufacturerInfo
from src.manufacturer.schemas import Manufacturer
from src.repository import CRUDRepository
from src.services import GenericServices
from src.sorting import apply_sorting_wrapper, SortingRelatedField, SortingRelatedFieldsMap, apply_sorting

filter_related_fields_map: FilterRelatedFieldsMap = {"name": FilterRelatedField(join=None, column=Manufacturer.name, use_exists=False)}
sorting_related_fields_map: SortingRelatedFieldsMap = {"name": SortingRelatedField(join=None, column=Manufacturer.name),}

class ManufacturerServices(GenericServices[Manufacturer, ManufacturerInfo]):
    def __init__(self):
        super().__init__(CRUDRepository(
            Manufacturer,
            filter_callback=apply_filters_wrapper(apply_filters, filter_related_fields_map),
            sorting_callback=apply_sorting_wrapper(apply_sorting, sorting_related_fields_map)
        ), ManufacturerInfo)