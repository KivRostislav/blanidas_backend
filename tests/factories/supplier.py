from faker.proxy import Faker
from polyfactory import Use, Ignore
from polyfactory.factories.pydantic_factory import ModelFactory
from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory

from src.supplier.models import SupplierCreate, SupplierUpdate
from src.supplier.schemas import Supplier
from tests.providers import UkrainePhoneProvider

faker = Faker(locale="uk_UA")
faker.add_provider(UkrainePhoneProvider)

class SupplierORMFactory(SQLAlchemyFactory[Supplier]):
    __faker__ = faker
    spare_parts = Ignore()

    contact_email = Use(faker.email)
    contact_phone = Use(faker.ukrainian_phone)

class SupplierCreateFactory(ModelFactory[SupplierCreate]):
    __faker__ = faker

    contact_email = Use(faker.email)
    contact_phone = Use(faker.ukrainian_phone)

class SupplierUpdateFactory(ModelFactory[SupplierUpdate]):
    __faker__ = faker

    contact_email = Use(faker.email)
    contact_phone = Use(faker.ukrainian_phone)
