from src.equipment.filters import apply_equipment_filters
from src.equipment.models import EquipmentInfo
from src.equipment.schemas import Equipment
from src.equipment_category.schemas import EquipmentCategory
from src.equipment_model.schemas import EquipmentModel
from src.filters import FilterRelatedField, apply_filters_wrapper, apply_filters
from src.institution.schemas import Institution
from src.manufacturer.schemas import Manufacturer
from src.repository import CRUDRepository
from src.services import GenericServices
from src.sorting import SortingRelatedField, apply_sorting_wrapper, apply_sorting

filter_related_fields_map = {
    "status": None,
    "equipment_model_name_or_serial_number": None,
    "institution_id": FilterRelatedField(join=None, column=Equipment.institution_id, use_exists=False),
    "equipment_category_id": FilterRelatedField(join=None, column=Equipment.equipment_category_id, use_exists=False),
    "manufacturer_id": FilterRelatedField(join=None, column=Equipment.manufacturer_id, use_exists=False),
}

sorting_related_fields_map = {
    "name": SortingRelatedField(join=Equipment.equipment_model, column=EquipmentModel.name),
    "institution_name": SortingRelatedField(join=Equipment.institution, column=Institution.name),
    "manufacturer_name": SortingRelatedField(join=Equipment.manufacturer, column=Manufacturer.name),
    "equipment_category_name": SortingRelatedField(join=Equipment.equipment_category, column=EquipmentCategory.name)
}

class EquipmentServices(GenericServices[Equipment, EquipmentInfo]):
    def __init__(self):
        super().__init__(CRUDRepository(
            Equipment,
            filter_callback=apply_filters_wrapper(apply_equipment_filters, filter_related_fields_map),
            sorting_callback=apply_sorting_wrapper(apply_sorting, sorting_related_fields_map)
        ), EquipmentInfo)