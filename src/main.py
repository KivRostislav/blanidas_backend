from contextlib import asynccontextmanager

from fastapi import FastAPI
from datetime import date

from sqlalchemy import and_, select

from .auth.models import ScopeCreate
from .auth.router import router as auth_router
from .auth.schemas import Scope, Role, EngineerScopes, ManagerScopes
from .auth.services import AuthServices, ScopeServices
from .database import engine, session_factory, BaseDatabaseModel
import src.auth.models as auth_models
import src.auth.schemas as auth_schemas

from src.mailer.subscriber import on_low_stock # need


from src.institution.router import router as institution_router
from src.institution_type.router import router as institution_type_router
from src.equipment_model.router import router as equipment_model_router
from src.equipment_category.router import router as equipment_category_router
from src.manufacturer.router import router as manufacturer_router
from src.supplier.router import router as supplier_router
from src.equipment.router import router as equipment_router
from src.spare_part_category.router import router as spare_part_category_router
from src.spare_part.router import router as spare_part_router
from src.repair_request.router import router as repair_request_router
from src.failure_type.router import router as failure_type_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    async with engine.begin() as connection:
        await connection.run_sync(BaseDatabaseModel.metadata.create_all)
    async with session_factory() as session:
        create_manager_scopes = [ScopeCreate(role=Role.manager, name=x).model_dump() for x in ManagerScopes]
        create_engineer_scopes = [ScopeCreate(role=Role.engineer, name=x).model_dump() for x in EngineerScopes]
        scope_services = ScopeServices()
        await scope_services.create_if_not_exist(create_manager_scopes, session)
        await scope_services.create_if_not_exist(create_engineer_scopes, session)
# healthy check sdfaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaadsafasdfsadfsfsafasdfdsafasd
        stmt = select(Scope).where(and_(
            Scope.role == auth_schemas.Role.manager,
            Scope.name.in_(auth_schemas.ManagerScopes),
        ))
        scopes = (await session.execute(stmt)).scalars().all()
        superuser = auth_models.UserCreate(
            username="",
            phone_number="+3800683456789",
            department="",
            workplace_id=None,
            hire_at=date.today(),
            email="admin@admin.com",
            password="admin1234",
            role=auth_schemas.Role.manager,
            scopes_ids=[scope.id for scope in scopes],
            receive_low_stock_notification=True,
            receive_repair_request_created_notification=True
        )
        auth_service = AuthServices()
        await auth_service.create_if_not_exists(
            data=superuser.model_dump(exclude_none=True),
            database=session,
            unique_fields=["username", "email"],
            relationship_fields=["scopes"],
        )
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
app.include_router(repair_request_router)
app.include_router(failure_type_router)
