from src.equipment_model.models import EquipmentModelInfo
from src.equipment_model.schemas import EquipmentModel
from src.filters import FilterRelatedField, apply_filters_wrapper, apply_filters
from src.repository import CRUDRepository
from src.services import GenericServices
from src.sorting import SortingRelatedField, apply_sorting_wrapper, apply_sorting

filter_related_fields_map = {"name": FilterRelatedField(join=None, column=EquipmentModel.name, use_exists=False)}
sorting_related_fields_map = {"name": SortingRelatedField(join=None, column=EquipmentModel.name)}

class EquipmentModelServices(GenericServices[EquipmentModel, EquipmentModelInfo]):
    def __init__(self):
        super().__init__(CRUDRepository(
            EquipmentModel,
            filter_callback = apply_filters_wrapper(apply_filters, filter_related_fields_map),
            sorting_callback = apply_sorting_wrapper(apply_sorting, sorting_related_fields_map)
        ), EquipmentModelInfo)