import faker
from faker.proxy import Faker
from polyfactory import Ignore, Use
from polyfactory.factories import DataclassFactory
from polyfactory.factories.pydantic_factory import ModelFactory
from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory

from src.institution.models import InstitutionCreate, InstitutionUpdate
from src.institution.schemas import Institution
from tests.providers import UkrainePhoneProvider

faker = Faker(locale="uk_UA")
faker.add_provider(UkrainePhoneProvider)

class InstitutionORMFactory(SQLAlchemyFactory[Institution]):
    __faker__ = faker

    institution_type = Ignore()
    equipment = Ignore()
    spare_parts = Ignore()

    contact_email = Use(faker.email)
    contact_phone = Use(faker.ukrainian_phone)

class InstitutionCreateFactory(ModelFactory[InstitutionCreate]):
    __faker__ = faker

    contact_email = Use(faker.email)
    contact_phone = Use(faker.ukrainian_phone)

class InstitutionUpdateFactory(ModelFactory[InstitutionUpdate]):
    __faker__ = faker

    contact_email = Use(faker.email)
    contact_phone = Use(faker.ukrainian_phone)
