from fastapi import status, Request
from fastapi.exceptions import RequestValidationError
from starlette.responses import JSONResponse

from src.exceptions import ErrorMap, ApiErrorCode, ApiError, DomainErrorCode

Pydantic_ERROR_MAP = {
    "value_error.contact_email": ErrorMap(code=ApiErrorCode.invalid_email_format, message="Невалідний формат email"),
    "value_error.contact_phone": ErrorMap(code=ApiErrorCode.invalid_phone_format, message="Невалідний формат телефону"),
    "value_error.phone_number": ErrorMap(code=ApiErrorCode.invalid_phone_format, message="Невалідний формат телефону"),
    "": ErrorMap(code=ApiErrorCode.invalid_value, message="Невалідна інформаці"),
}

async def error_handler(request: Request, call_next):
    try:
        response = await call_next(request)
    except ApiError as exc:
        mapped_error = exc.error_map[exc.code][exc.field]
        status_code = status.HTTP_400_BAD_REQUEST
        if exc.code == DomainErrorCode.not_entity:
            status_code = status.HTTP_404_NOT_FOUND

        return JSONResponse(status_code=status_code, content={
            "code": mapped_error.code,
            "message": mapped_error.message,
            "fields": exc.field,
        })
    except Exception:
        raise
        # return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})
    return response

async def validation_exception_handler(_: Request, exc: RequestValidationError):
    error = exc.errors()[0]
    key = f"{error['type']}.{error['loc'][-1]}"
    mapper = Pydantic_ERROR_MAP.get(key, Pydantic_ERROR_MAP[""])
    return JSONResponse(status_code=422, content={"code": mapper.code, "message": mapper.message})

