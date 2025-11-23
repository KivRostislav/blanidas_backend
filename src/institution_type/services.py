from src.institution_type.models import InstitutionTypeInfo
from src.institution_type.schemas import InstitutionType
from src.repository import CRUDRepository
from src.services import GenericServices

class InstitutionTypeServices(GenericServices[InstitutionType, InstitutionTypeInfo]):
    def __init__(self):
        super().__init__(CRUDRepository(InstitutionType), InstitutionTypeInfo)

