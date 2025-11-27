from polyfactory import Ignore
from polyfactory.factories.pydantic_factory import ModelFactory
from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory

from src.equipment_model.models import EquipmentModelCreate, EquipmentModelUpdate
from src.equipment_model.schemas import EquipmentModel


class EquipmentModelORMFactory(SQLAlchemyFactory[EquipmentModel]):
    equipment = Ignore()
    spare_parts = Ignore()

class EquipmentModelCreateFactory(ModelFactory[EquipmentModelCreate]):
    pass

class EquipmentModelUpdateFactory(ModelFactory[EquipmentModelUpdate]):
    pass
