from src.failure_type.models import FailureTypeInfo
from src.failure_type.schemas import FailureType
from src.filters import apply_filters_wrapper, apply_filters, FilterRelatedField
from src.repository import CRUDRepository
from src.services import GenericServices
from src.sorting import SortingRelatedField, apply_sorting_wrapper, apply_sorting

filter_related_fields_map = {"name": FilterRelatedField(join=None, column=FailureType.name, use_exists=False)}
sorting_related_fields_map = {"name": SortingRelatedField(join=None, column=FailureType.name)}


class FailureTypeServices(GenericServices[FailureType, FailureTypeInfo]):
    def __init__(self):
        super().__init__(CRUDRepository(
            FailureType,
            filter_callback=apply_filters_wrapper(apply_filters, filter_related_fields_map),
            sorting_callback=apply_sorting_wrapper(apply_sorting, sorting_related_fields_map)
        ), FailureTypeInfo)
