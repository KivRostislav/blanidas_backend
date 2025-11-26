from datetime import date
from polyfactory import Ignore, Use
from polyfactory.factories.pydantic_factory import ModelFactory
from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory

from src.equipment.models import EquipmentCreate, EquipmentUpdate
from src.equipment.schemas import Equipment


class EquipmentORMFactory(SQLAlchemyFactory[Equipment]):
    installed = Use(lambda : date.today())

    institution = Ignore()
    equipment_model = Ignore()
    equipment_category = Ignore()
    manufacturer = Ignore()

class EquipmentCreateFactory(ModelFactory[EquipmentCreate]):
    installed = Use(lambda: date.today())

class EquipmentUpdateFactory(ModelFactory[EquipmentUpdate]):
    installed = Use(lambda: date.today())