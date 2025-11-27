from src.repository import CRUDRepository
from src.services import GenericServices
from src.spare_part.models import SparePartInfo
from src.spare_part.schemas import SparePart


class SparePartServices(GenericServices[SparePart, SparePartInfo]):
    def __init__(self):
        super().__init__(CRUDRepository(SparePart), SparePartInfo)