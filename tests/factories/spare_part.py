from polyfactory import Ignore
from polyfactory.factories.pydantic_factory import ModelFactory
from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory
from src.spare_part.models import SparePartUpdate, SparePartCreate
from src.spare_part.schemas import SparePart

class SparePartORMFactory(SQLAlchemyFactory[SparePart]):
    supplier = Ignore()
    institution = Ignore()
    spare_part_category = Ignore()
    manufacturer = Ignore()
    compatible_models = Ignore()

class SparePartCreateFactory(ModelFactory[SparePartCreate]):
    pass

class SparePartUpdateFactory(ModelFactory[SparePartUpdate]):
    pass
