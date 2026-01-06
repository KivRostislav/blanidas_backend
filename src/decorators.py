from functools import wraps
from typing import ParamSpec, TypeVar, Callable, Awaitable

from sqlalchemy.exc import IntegrityError

from src.exceptions import DomainError, ApiError, ErrorsMap, parse_integrity_error

P = ParamSpec("P")
R = TypeVar("R")

def domain_errors(errors_map: ErrorsMap):
    def decorator(func: Callable[P, Awaitable[R]]) -> Callable[P, Awaitable[R]]:
        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            try:
                return await func(*args, **kwargs)
            except DomainError as e:
                raise ApiError(e, errors_map)
        return wrapper
    return decorator

def integrity_errors():
    def decorator(func: Callable[P, Awaitable[R]]) -> Callable[P, Awaitable[R]]:
        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            try:
                return await func(*args, **kwargs)
            except IntegrityError as e:
                error = parse_integrity_error(e)
                if error is None: raise
                raise error
        return wrapper
    return decorator