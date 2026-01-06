from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from datetime import date

from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from sqlalchemy import and_, select
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from src.auth.services import AuthServices
from src.config import get_settings
from src.database import session_factory, BaseDatabaseModel
import src.auth.models as auth_models
import src.auth.schemas as auth_schemas

from src.mailer.subscriber import on_low_stock, on_repair_request_created # need

from src.router import router

from .exceptions import DomainError, NotFoundError, ApiError, ErrorCode, ErrorMap


@asynccontextmanager
async def lifespan(_: FastAPI):
    """ async with session_factory() as session:
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
    """
    yield

app = FastAPI(lifespan=lifespan)
app.include_router(router)

Pydantic_ERROR_MAP = {
    "value_error.contact_email": ErrorMap(code="invalid email", message="Невалідний формат email"),
    "value_error.contact_phone": ErrorMap(code="invalid phone", message="Невалідний формат телефону"),
    "": ErrorMap(code="invalid value", message="Невалідна інформаці"),
}

@app.middleware("http")
async def error_handler(request: Request, call_next):
    try:
        response = await call_next(request)
    except ApiError as exc:
        mapped_error = exc.error_map[exc.code][exc.field]
        status_code = status.HTTP_400_BAD_REQUEST
        if exc.code == ErrorCode.not_entity:
            status_code = status.HTTP_404_NOT_FOUND

        return JSONResponse(status_code=status_code, content={"code": mapped_error.code, "message": mapped_error.message})
    except Exception:
        raise
        # return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})
    return response

# @app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    error = exc.errors()[0]
    key = f"{error['type']}.{error['loc'][-1]}"
    mapper = Pydantic_ERROR_MAP.get(key, Pydantic_ERROR_MAP[""])
    return JSONResponse(status_code=422, content={"code": mapper.code, "message": mapper.message})


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)