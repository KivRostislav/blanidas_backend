from polyfactory import Ignore
from polyfactory.factories.pydantic_factory import ModelFactory
from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory

from src.institution_type.models import InstitutionTypeCreate, InstitutionTypeUpdate
from src.institution_type.schemas import InstitutionType

class InstitutionTypeORMFactory(SQLAlchemyFactory[InstitutionType]):
    institutions = Ignore()

class InstitutionTypeCreateFactory(ModelFactory[InstitutionTypeCreate]):
    pass

class InstitutionTypeUpdateFactory(ModelFactory[InstitutionTypeUpdate]):
    pass
