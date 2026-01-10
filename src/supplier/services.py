from src.filters import FilterRelatedField, apply_filters_wrapper, apply_filters
from src.repository import CRUDRepository
from src.services import GenericServices
from src.sorting import SortingRelatedField, apply_sorting_wrapper, apply_sorting
from src.supplier.models import SupplierInfo
from src.supplier.schemas import Supplier

filter_related_fields_map = {"name": FilterRelatedField(column=Supplier.name)}
sorting_related_fields_map = {"name": SortingRelatedField(column=Supplier.name) }

class SupplierServices(GenericServices[Supplier, SupplierInfo]):
    def __init__(self):
        super().__init__(CRUDRepository(
            Supplier,
            filter_callback = apply_filters_wrapper(apply_filters, filter_related_fields_map),
            sorting_callback = apply_sorting_wrapper(apply_sorting, sorting_related_fields_map),
        ), SupplierInfo)

