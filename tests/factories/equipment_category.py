from polyfactory import Ignore
from polyfactory.factories.pydantic_factory import ModelFactory
from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory

from src.equipment_category.models import EquipmentCategoryCreate, EquipmentCategoryUpdate
from src.equipment_category.schemas import EquipmentCategory


class EquipmentCategoryORMFactory(SQLAlchemyFactory[EquipmentCategory]):
    equipment = Ignore()

class EquipmentCategoryCreateFactory(ModelFactory[EquipmentCategoryCreate]):
    pass

class EquipmentCategoryUpdateFactory(ModelFactory[EquipmentCategoryUpdate]):
    pass
