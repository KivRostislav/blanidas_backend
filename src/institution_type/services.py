from src.filters import FilterRelatedField, apply_filters_wrapper, apply_filters
from src.institution_type.models import InstitutionTypeInfo
from src.institution_type.schemas import InstitutionType
from src.repository import CRUDRepository
from src.services import GenericServices
from src.sorting import SortingRelatedField, apply_sorting_wrapper, apply_sorting

filter_related_fields_map = {"name": FilterRelatedField(join=None, column=InstitutionType.name, use_exists=False)}
sorting_related_fields_map = {"name": SortingRelatedField(join=None, column=InstitutionType.name)}

class InstitutionTypeServices(GenericServices[InstitutionType, InstitutionTypeInfo]):
    def __init__(self):
        super().__init__(CRUDRepository(
            InstitutionType,
            filter_callback=apply_filters_wrapper(apply_filters, filter_related_fields_map),
            sorting_callback=apply_sorting_wrapper(apply_sorting, sorting_related_fields_map),
        ), InstitutionTypeInfo)

