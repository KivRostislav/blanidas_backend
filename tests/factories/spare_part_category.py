from polyfactory import Ignore
from polyfactory.factories.pydantic_factory import ModelFactory
from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory

from src.spare_part_category.models import SparePartCategoryCreate, SparePartCategoryUpdate
from src.spare_part_category.schemas import SparePartCategory


class SparePartCategoryORMFactory(SQLAlchemyFactory[SparePartCategory]):
    spare_parts = Ignore()

class SparePartCategoryCreateFactory(ModelFactory[SparePartCategoryCreate]):
    pass

class SparePartCategoryUpdateFactory(ModelFactory[SparePartCategoryUpdate]):
    pass