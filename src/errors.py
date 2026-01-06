from functools import wraps
from typing import Type, TypeVar, ParamSpec, Callable, Awaitable
from src.exceptions import ErrorsMap, DomainError, ApiError

TParams = ParamSpec("TParams")
TReturn = TypeVar("TReturn")
TError = TypeVar("TError")

def error_wrapper(
        error_type: TError,
        func: Callable[TParams, Awaitable[TReturn]],
        except_func: Callable[[TError], None]
) -> Callable[TParams, Awaitable[TReturn]]:
    @wraps(func)
    async def wrapper(*args: TParams.args, **kwargs: TParams.kwargs) -> TReturn:
        try:
            return await func(*args, **kwargs)
        except error_type as e:
            except_func(e)
    return wrapper

def domain_error_wrapper(
        func: Callable[TParams, Awaitable[TReturn]],
        errors_map: ErrorsMap
) -> Callable[TParams, Awaitable[TReturn]]:
    return error_wrapper(DomainError, func, lambda e: raise ApiError(e, errors_map))

