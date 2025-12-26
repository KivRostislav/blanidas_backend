from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from datetime import date

from sqlalchemy import and_, select
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from src.auth.models import ScopeCreate
from src.auth.schemas import Scope, Role, EngineerScopes, ManagerScopes
from src.auth.services import AuthServices, ScopeServices
from src.config import get_settings
from src.database import session_factory, BaseDatabaseModel
import src.auth.models as auth_models
import src.auth.schemas as auth_schemas

from src.mailer.subscriber import on_low_stock, on_repair_request_created # need

from src.router import router

from .exceptions import DomainError, NotFoundError

@asynccontextmanager
async def lifespan(_: FastAPI):
    async with session_factory() as session:
        create_manager_scopes = [ScopeCreate(role=Role.manager, name=x).model_dump() for x in ManagerScopes]
        create_engineer_scopes = [ScopeCreate(role=Role.engineer, name=x).model_dump() for x in EngineerScopes]
        scope_services = ScopeServices()
        await scope_services.create_if_not_exist(create_manager_scopes, session)
        await scope_services.create_if_not_exist(create_engineer_scopes, session)
        stmt = select(Scope).where(and_(
            Scope.role == auth_schemas.Role.manager,
            Scope.name.in_(auth_schemas.ManagerScopes),
        ))
        scopes = (await session.execute(stmt)).scalars().all()
        settings = get_settings()
        superuser = auth_models.UserCreate(
            username="",
            phone_number="+380686894116",
            department="",
            workplace_id=None,
            hire_at=date.today(),
            email=settings.superuser_email,
            password=settings.superuser_password,
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
app.include_router(router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*", "http://localhost:5174/"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# @app.middleware("http")
async def error_handler(request: Request, call_next):
    try:
        response = await call_next(request)
    except DomainError as exc:
        status_code = status.HTTP_400_BAD_REQUEST
        if isinstance(exc, NotFoundError):
            status_code = status.HTTP_404_NOT_FOUND
        return JSONResponse(status_code=status_code, content={"detail": exc.message})
    except Exception:
        return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})
    return response