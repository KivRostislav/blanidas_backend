from src.manufacturer.models import ManufacturerInfo
from src.manufacturer.schemas import Manufacturer
from src.repository import CRUDRepository
from src.services import GenericServices


class ManufacturerServices(GenericServices[Manufacturer, ManufacturerInfo]):
    def __init__(self):
        super().__init__(CRUDRepository(Manufacturer), ManufacturerInfo)