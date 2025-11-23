from src.institution.models import InstitutionInfo
from src.institution.schemas import Institution
from src.repository import CRUDRepository
from src.services import GenericServices


class InstitutionServices(GenericServices[Institution, InstitutionInfo]):
    def __init__(self):
        super().__init__(CRUDRepository(Institution), InstitutionInfo)