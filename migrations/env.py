import asyncio
from logging.config import fileConfig

import sys
import os

from sqlalchemy.ext.asyncio import create_async_engine

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from alembic import context

from src.database import BaseDatabaseModel
from src.config import AppSettings

from src.institution.schemas import Institution
from src.institution_type.schemas import InstitutionType
from src.equipment_model.schemas import EquipmentModel
from src.equipment_category.schemas import EquipmentCategory
from src.manufacturer.schemas import Manufacturer
from src.supplier.schemas import Supplier
from src.equipment.schemas import Equipment
from src.spare_part_category.schemas import SparePartCategory
from src.spare_part.schemas import SparePart
from src.repair_request.schemas import RepairRequest
from src.failure_type.schemas import FailureType
from src.auth.schemas import User, Scope


config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

settings = AppSettings()
config.set_main_option("sqlalchemy.url", settings.database_url)
target_metadata = BaseDatabaseModel.metadata

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online_async() -> None:
    connectable = create_async_engine(
        config.get_main_option("sqlalchemy.url"),
        poolclass=None,
    )

    async with connectable.begin() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()

def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    asyncio.run(run_migrations_online_async())

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
