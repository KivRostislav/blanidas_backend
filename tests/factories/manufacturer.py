from polyfactory import Ignore
from polyfactory.factories.pydantic_factory import ModelFactory
from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory
from polyfactory.pytest_plugin import register_fixture

from src.manufacturer.schemas import Manufacturer
from src.manufacturer.models import ManufacturerUpdate, ManufacturerCreate

class ManufacturerORMFactory(SQLAlchemyFactory[Manufacturer]):
    equipment = Ignore()
    spare_parts = Ignore()

class ManufacturerCreateFactory(ModelFactory[ManufacturerCreate]):
    pass

class ManufacturerUpdateFactory(ModelFactory[ManufacturerUpdate]):
    pass

def register_factories() -> None:
    register_fixture(ManufacturerCreateFactory)
    register_fixture(ManufacturerUpdateFactory)
    register_fixture(ManufacturerORMFactory)

