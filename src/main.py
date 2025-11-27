from contextlib import asynccontextmanager

from fastapi import FastAPI
from datetime import date

from .auth.models import ScopesCreate
from .auth.router import router as auth_router
from .database import engine, session_factory, BaseDatabaseModel

import src.auth.services as auth_services
import src.auth.models as auth_models
import src.auth.schemas as auth_schemas


from src.institution.router import router as institution_router
from src.institution_type.router import router as institution_type_router
from src.equipment_model.router import router as equipment_model_router
from src.equipment_category.router import router as equipment_category_router
from src.manufacturer.router import router as manufacturer_router
from src.supplier.router import router as supplier_router
from src.equipment.router import router as equipment_router
from src.spare_part_category.router import router as spare_part_category_router
from src.spare_part.router import router as spare_part_router

@asynccontextmanager
async def lifespan(_: FastAPI):
    async with engine.begin() as connection:
        await connection.run_sync(BaseDatabaseModel.metadata.create_all)
    async with session_factory() as session:
        create_manager_scopes = ScopesCreate(
            role=auth_schemas.Role.manager, scopes=[x for x in auth_schemas.ManagerScopes]
        )
        create_engineer_scopes = ScopesCreate(
            role=auth_schemas.Role.engineer, scopes=[x for x in auth_schemas.EngineerScopes]
        )
        await auth_services.create_scopes_if_not_exist(create_manager_scopes, session)
        await auth_services.create_scopes_if_not_exist(create_engineer_scopes, session)

        superuser = auth_models.UserCreate(
                username="",
                phone_number="+3800683456789",
                department="",
                workplace_id=None,
                hire_at=date.today(),
                email="admin@admin.com",
                password="admin1234",
                role=auth_schemas.Role.manager,
                scopes=[scope for scope in auth_schemas.ManagerScopes]
        )
        await auth_services.create_user_if_not_exist(superuser, session)
    yield

app = FastAPI(lifespan=lifespan)


app.include_router(institution_router)
app.include_router(institution_type_router)
app.include_router(equipment_model_router)
app.include_router(equipment_category_router)
app.include_router(manufacturer_router)
app.include_router(equipment_router)

app.include_router(auth_router)
app.include_router(institution_type_router)
app.include_router(supplier_router)
app.include_router(spare_part_category_router)
app.include_router(spare_part_router)





