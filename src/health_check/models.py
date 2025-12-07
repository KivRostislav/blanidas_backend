from enum import Enum

from pydantic import BaseModel


class HealthCheckResponseStatus(str, Enum):
    ok = "ok"
    error = "error"

class HealthCheckResponse(BaseModel):
    status: HealthCheckResponseStatus