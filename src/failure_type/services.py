from src.failure_type.models import FailureTypeInfo
from src.failure_type.schemas import FailureType
from src.repository import CRUDRepository
from src.services import GenericServices


class FailureTypeServices(GenericServices[FailureType, FailureTypeInfo]):
    def __init__(self):
        super().__init__(CRUDRepository(FailureType), FailureTypeInfo)
