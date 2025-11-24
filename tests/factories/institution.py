from polyfactory import Ignore
from polyfactory.factories.pydantic_factory import ModelFactory
from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory

from src.institution.models import InstitutionCreate, InstitutionUpdate
from src.institution.schemas import Institution

class InstitutionORMFactory(SQLAlchemyFactory[Institution]):
    institution_type = Ignore()
    equipment = Ignore()

class InstitutionCreateFactory(ModelFactory[InstitutionCreate]):
    pass

class InstitutionUpdateFactory(ModelFactory[InstitutionUpdate]):
    pass
