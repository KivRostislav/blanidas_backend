from src.filters import FilterRelatedField, apply_filters_wrapper
from src.institution.filters import apply_institution_filters
from src.institution.models import InstitutionInfo
from src.institution.schemas import Institution
from src.repository import CRUDRepository
from src.services import GenericServices
from src.sorting import SortingRelatedField, apply_sorting_wrapper, apply_sorting

filterRelatedFieldsMap = {"name_or_address": None}

sortingRelatedFieldsMap = {"name": SortingRelatedField(join=None, column=Institution.name)}

class InstitutionServices(GenericServices[Institution, InstitutionInfo]):
    def __init__(self):
        super().__init__(CRUDRepository(
            Institution,
            filter_callback=apply_filters_wrapper(apply_institution_filters, filterRelatedFieldsMap),
            sorting_callback=apply_sorting_wrapper(apply_sorting, sortingRelatedFieldsMap)
        ), InstitutionInfo)