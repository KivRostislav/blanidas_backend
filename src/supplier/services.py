from src.repository import CRUDRepository
from src.services import GenericServices
from src.supplier.models import SupplierInfo
from src.supplier.schemas import Supplier


class SupplierServices(GenericServices[Supplier, SupplierInfo]):
    def __init__(self):
        super().__init__(CRUDRepository(Supplier), SupplierInfo)

